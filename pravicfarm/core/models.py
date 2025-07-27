from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('live_birds', 'Live Birds'),
        ('eggs', 'Eggs'),
        ('processed_meat', 'Processed Meat'),
        ('feeds', 'Feeds & Supplements'),
        ('equipment', 'Equipment'),
        ('training', 'Training/Consultancy'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    negotiable = models.BooleanField(default=False)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, default='Pravic Poultry')

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    quantity = models.PositiveIntegerField(default=1)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    order_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_method = models.CharField(
        max_length=20,
        choices=[('ecocash', 'EcoCash'), ('paynow', 'PayNow'), ('cash', 'Cash on Delivery')],
        default='cash'
    )
    is_paid = models.BooleanField(default=False)

    def cancel_order(self):
            self.status = 'cancelled'
            self.save()
    
    def restore_stock(self):
        for item in self.orderitem_set.all():
            item.product.stock += item.quantity
            item.product.save()

    def __str__(self):
        return f"Order {self.id}"
    def __str__(self):
        return f"Order {self.order_reference} - {self.customer_name}"
    
    def get_total(self):
         return self.product.price * self.quantity

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"    

class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject

class GalleryImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title    