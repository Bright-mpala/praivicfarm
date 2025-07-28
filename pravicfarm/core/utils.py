# core/utils.py

import qrcode
from io import BytesIO
import base64
from reportlab.pdfgen import canvas
import urllib.parse
from .models import Order
from io import BytesIO
import base64
import urllib.parse

def generate_ecocash_ussd_qr(amount):
    receiver = "0780808201"  # Your Ecocash number with leading 0
    # Format USSD code with trailing #
    ussd_code = f"*151*1*1*{receiver}*{amount}#"
    # URL encode the USSD string for tel: URI
    ussd_encoded = urllib.parse.quote(ussd_code, safe='')
    tel_uri = f"tel:{ussd_encoded}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(tel_uri)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def generate_order_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, 800, "Pravic Poultry Farm")
    p.setFont("Helvetica", 12)
    p.drawString(50, 760, f"Order Reference: {order.order_reference}")
    p.drawString(50, 740, f"Customer: {order.customer_name}")
    p.drawString(50, 720, f"Product: {order.product.name}")
    p.drawString(50, 700, f"Quantity: {order.quantity}")
    p.drawString(50, 680, f"Payment Method: {order.payment_method}")
    p.drawString(50, 660, f"Total Price: ${order.product.price * order.quantity:.2f}")

    p.drawString(50, 620, f"Delivery Address:")
    p.drawString(70, 600, order.address)

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
from django.utils import timezone
from datetime import timedelta

def mark_expired_orders(expiry_days=7):
    cutoff = timezone.now() - timedelta(days=expiry_days)
    expired_orders = Order.objects.filter(is_attended=False, order_date__lt=cutoff, expired=False)
    expired_orders.update(expired=True)
