from django.contrib import admin
from .models import BlogPost, ContactMessage, Subscriber, Product, Order, OrderItem, GalleryImage, Review
import csv
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__order_reference', 'user__username', 'comment')
    readonly_fields = ('created_at',)

    # Optional: Add inline editing of comments and ratings
    fields = ('order', 'user', 'rating', 'comment', 'created_at')
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):   
    list_display = ('name', 'category', 'price', 'available', 'created_at')
    search_fields = ('name', 'category')
    list_filter = ('category', 'available')

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):   
    list_display = ('title', 'uploaded_at',)
    list_filter = ('title', 'description')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'author')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')
    list_filter = ('published_date',)
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'responded', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('responded', 'created_at')
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    list_filter = ('subscribed_at',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'customer_email', 'order_date', 'is_attended', 'expired')
    list_editable = ('is_attended',)
    list_filter = ('is_attended', 'expired', 'order_date')
    search_fields = ('customer_email', 'product__name', 'customer_name')
    inlines = [OrderItemInline]
    actions = ['mark_as_confirmed', 'export_to_csv']

    def status_colored(self, obj):
        color_map = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            color_map.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='CONFIRMED')
        self.message_user(request, f"{updated} order(s) marked as confirmed.")

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)

        writer.writerow(['Customer Name', 'Email', 'Phone', 'Status', 'Date'])

        for order in queryset:
            writer.writerow([
                order.customer_name,
                order.customer_email,
                order.phone,
                order.status,
                order.order_date,
            ])

        return response
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at')
    search_fields = ('subject',)    


@admin.action(description="Mark selected orders as Paid")
def mark_as_paid(modeladmin, request, queryset):
    queryset.update(is_paid=True)