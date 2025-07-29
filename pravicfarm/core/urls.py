from django.views import View
from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required
from .views import CancelOrderView


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('order/', views.order_view, name='order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_post_detail, name='blog_post_detail'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/', views.products, name='products'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', CancelOrderView.as_view(), name='cancel_order'),
    path('admin/send-newsletter/', views.send_newsletter, name='send_newsletter'),
    path('order/<int:order_id>/receipt/', views.order_receipt_pdf, name='order_receipt_pdf'),
    path('accounts/', include('allauth.urls')), 
    path('accounts/', include('allauth.socialaccount.urls')),
    path('gallery/', views.gallery, name='gallery'),
    path('order/<int:order_id>/review/', views.review_view, name='review'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
]
