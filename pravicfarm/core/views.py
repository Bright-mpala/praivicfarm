import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now, timezone
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, BlogPost, ContactMessage, Subscriber, Order, Newsletter, GalleryImage, Review
from allauth.account.forms import LoginForm, SignupForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils import generate_ecocash_ussd_qr, generate_order_pdf, mark_expired_orders
from django.db import transaction
from django.http import FileResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

@require_http_methods(["GET"])
def index(request):
    products = Product.objects.filter(available=True)
    blog_posts = BlogPost.objects.order_by('-published_date')[:3]
    products = Product.objects.filter(available=True).order_by('-created_at')[:3]  
    gallery = GalleryImage.objects.all().order_by('-uploaded_at')[:6]  # Fetch latest 6 images
    return render(request, 'core/index.html', {
        'products': products,
        'blog_posts': blog_posts,
        'products': products,
        'gallery': gallery,
    })

# About
@require_http_methods(["GET"])
def about(request):
    return render(request, 'core/about.html')

# Contact
@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if not (name and email and message):
            messages.error(request, 'Please fill in all fields.')
            return redirect('home')

        ContactMessage.objects.create(name=name, email=email, message=message)

        admin_html = render_to_string('emails/admin_message.html', {
            'name': name,
            'email': email,
            'message': message,
        })

        admin_msg = EmailMultiAlternatives(
            subject=f'New Contact Message from {name}',
            body='',
            from_email=f'{name} <{email}>',
            to=[settings.CONTACT_NOTIFY_EMAIL],
            reply_to=[email]
        )
        admin_msg.attach_alternative(admin_html, 'text/html')
        admin_msg.send()

        user_html = render_to_string('emails/user_autoresponse.html', {'name': name})
        user_msg = EmailMultiAlternatives(
            subject='Thank You for Contacting Pravic',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        user_msg.attach_alternative(user_html, 'text/html')
        user_msg.send()

        messages.success(request, 'Your message was sent successfully!')
        return redirect('index')
    return redirect('index')

# Subscribe to Newsletter
@require_http_methods(["POST"])
def subscribe(request):
    email = request.POST.get('email')
    if not Subscriber.objects.filter(email=email).exists():
        Subscriber.objects.create(email=email)

        html_content = render_to_string('emails/email_confirmation.html', {
            'user': {'username': email.split('@')[0]},
            'current_year': now().year
        })

        email_msg = EmailMessage(
            subject="You're subscribed to Pravic Poultry 🐔",
            body=html_content,
            to=[email]
        )
        email_msg.content_subtype = 'html'
        email_msg.send()

        messages.success(request, "Thank you for subscribing to our newsletter!")
    else:
        messages.info(request, "You are already subscribed.")
    return redirect('/')

# Place Order
def order_view(request):
    products = Product.objects.filter(available=True, stock__gt=0)
    warning = None
    error = None

    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 1))
        customer_email = request.POST.get('customer_email')
        payment_method = request.POST.get('payment_method')
        ecocash_number = request.POST.get('ecocash_number')

        # Rate limit
        one_hour_ago = now() - timedelta(hours=1)
        recent_orders = Order.objects.filter(customer_email=customer_email, order_date__gte=one_hour_ago).count()
        if recent_orders >= 3:
            error = "You have made too many orders recently. Please try again later."
            return render(request, 'core/order.html', {'products': products, 'error': error})

        # Validate email early
        try:
            validate_email(customer_email)
        except ValidationError:
            error = "Invalid email address provided."
            return render(request, 'core/order.html', {'products': products, 'error': error})

        if payment_method == 'Ecocash' and not ecocash_number:
            error = "Please provide your Ecocash number."
            return render(request, 'core/order.html', {'products': products, 'error': error})

        try:
            with transaction.atomic():
                product = Product.objects.select_for_update().get(id=product_id)

                if product.stock < quantity:
                    warning = f"Only {product.stock} units of {product.name} left in stock."
                    return render(request, 'core/order.html', {'products': products, 'warning': warning})

                order = Order.objects.create(
                    product=product,
                    customer_name=request.POST.get('customer_name'),
                    customer_email=customer_email,
                    quantity=quantity,
                    phone=request.POST.get('phone'),
                    address=request.POST.get('address'),
                    payment_method=payment_method,
                    is_paid=(payment_method == 'cash'),
                    ecocash_number=ecocash_number if payment_method == 'Ecocash' else None
                )

                product.stock -= quantity
                product.save()
               
                review_exists = Review.objects.filter(order=order).exists()
                # Send confirmation email
                subject = 'Order Confirmation - Pravic Poultry Farm'
                html_message = render_to_string('emails/order_confirmation.html', {'order': order})
                plain_message = strip_tags(html_message)
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [customer_email], html_message=html_message)

                # Admin notification
                admin_subject = f"New Order #{order.order_reference}"
                admin_message = (
                    f"New order placed:\n\n"
                    f"Customer: {order.customer_name}\n"
                    f"Product: {order.product.name}\n"
                    f"Quantity: {order.quantity}\n"
                    f"Email: {order.customer_email}\n"
                    f"Phone: {order.phone}\n"
                    f"Address: {order.address}\n"
                    f"Payment Method: {order.payment_method}"
                )
                send_mail(admin_subject, admin_message, settings.DEFAULT_FROM_EMAIL, ['infopraivicfarm@gmail.com'])

                # WhatsApp link for session if needed
                whatsapp_number = "263780808201"
                whatsapp_message = f"Hi, I’ve ordered {order.quantity} x {order.product.name}. Order Ref: {order.order_reference}"
                whatsapp_url = f"https://wa.me/{whatsapp_number}?text={whatsapp_message.replace(' ', '%20')}"
                request.session['whatsapp_url'] = whatsapp_url

                # Handle response based on payment method
                if payment_method == 'Ecocash':
                    total = product.price * quantity
                    qr_code_data_uri = generate_ecocash_ussd_qr(total)
                    context = {
                        'products': products,
                        'order': order,
                        'review_exists': review_exists,
                        'success': True,
                        'ecocash_qr': qr_code_data_uri,
                    }
                    return render(request, 'core/order.html', context)
                else:
                    return redirect('order_success', order_id=order.id)

        except Product.DoesNotExist:
            error = "Selected product does not exist."

    return render(request, 'core/order.html', {
        'products': products,
        'warning': warning,
        'error': error
    })

@login_required
def order_success(request, order_id):
    whatsapp_url = request.session.get('whatsapp_url')
    order = get_object_or_404(Order, id=order_id, customer_email=request.user.email)
    review_exists = Review.objects.filter(order=order).exists()
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.user = request.user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('thank_you')
    return render(request, 'core/order_success.html', {
        'order': order,
        'whatsapp_url': whatsapp_url,
        'review_exists': review_exists
    })


# Blog listing
@require_http_methods(["GET"])
def blog(request):
    blog_posts = BlogPost.objects.order_by('-published_date')
    return render(request, 'core/blog.html', {'blog_posts': blog_posts})

# Blog post detail
@require_http_methods(["GET"])
def blog_post_detail(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'core/blog_post_detail.html', {'blog_post': blog_post})

# Product detail
@require_http_methods(["GET"])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'core/product_detail.html', {'product': product})

# Product listing
@require_http_methods(["GET"])
def products(request):
    category_filter = request.GET.get('category')
    product_list = Product.objects.filter(available=True)

    if category_filter:
        product_list = product_list.filter(category=category_filter)

    paginator = Paginator(product_list, 6)  # Show 6 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Product.CATEGORY_CHOICES

    return render(request, 'core/products.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_filter,
    })

# Send newsletter
@staff_member_required
def send_newsletter(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Newsletter.objects.create(subject=subject, message=message)

        recipients = [s.email for s in Subscriber.objects.all()]
        if recipients:
            EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                bcc=recipients
            ).send()
            messages.success(request, "Newsletter sent and saved.")
        else:
            messages.warning(request, "No subscribers found.")
        return redirect('/')

    return render(request, 'core/send_newsletter.html')


@login_required
def my_orders(request):
    # Mark expired orders before fetching (optional)
    mark_expired_orders(expiry_days=7)

    # Show only active (non-expired) orders
    orders = Order.objects.filter(
        customer_email=request.user.email,
        expired=False
    ).order_by('-order_date')

    if not orders.exists():
        messages.info(request, "You have no active orders yet.")

    return render(request, 'core/my_orders.html', {'orders': orders})


class CancelOrderView(LoginRequiredMixin, View):
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, customer_email=request.user.email)
        
        if order.status == 'PENDING':
            product = order.product
            product.stock += order.quantity
            product.save()
            order.status = 'CANCELLED'
            order.save()
            messages.success(request, "Your order has been cancelled and stock restored.")
        else:
            messages.warning(request, "This order cannot be cancelled.")
        
        return redirect('my_orders')
    
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_order_update(data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'orders',
        {
            'type': 'send_order_update',
            'content': data
        }
    )
send_order_update({'orders': 'Order list updated'})

def gallery(request):
    images = GalleryImage.objects.all().order_by('-uploaded_at')
    return render(request, 'core/gallery.html', {'images': images})
#order recipt
def order_receipt_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pdf_buffer = generate_order_pdf(order)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f'order_{order.order_reference}.pdf')

#Reviews
from .forms import ReviewForm

@login_required
def review_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.customer_email != request.user.email:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        return redirect('home')

    try:
        review = Review.objects.get(order=order, user=request.user)
    except Review.DoesNotExist:
        review = None

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review_obj = form.save(commit=False)
            review_obj.order = order
            review_obj.user = request.user
            review_obj.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'errors': form.errors}, status=400)

    return render(request, 'core/review.html', {'form': form, 'order': order})

def thank_you_view(request):
    return render(request, 'core/thank_you.html')
