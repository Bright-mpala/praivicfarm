from django.core.management.base import BaseCommand
from core.utils import mark_expired_orders

class Command(BaseCommand):
    help = 'Marks unattended orders as expired after expiry period'

    def handle(self, *args, **kwargs):
        mark_expired_orders(expiry_days=7)
        self.stdout.write("Expired orders marked successfully.")
