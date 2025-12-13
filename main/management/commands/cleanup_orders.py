from django.core.management import BaseCommand
from django.utils import timezone
from datetime import timedelta

from main.models import Order
from main.views import cancel_bonuses_payment


class Command(BaseCommand):
    help = ('Clean up PENDING orders older than 15 minutes')

    def handle(self, *args, **kwargs):
        threshold_time = timezone.now() - timedelta(minutes=15)
        stuck_orders = Order.objects.filter(status=Order.OrderStatus.PENDING, created_at__lte=threshold_time)

        count = stuck_orders.count()

        if count == 0:
            self.stdout.write(f"No pending orders older than 15 minutes")
            return

        self.stdout.write(f"Found {count} pending orders older than 15 minutes")

        for order in stuck_orders:
            try:
                cancel_bonuses_payment(order.id)
                self.stdout.write(self.style.SUCCESS(f"Canceled order #{order.id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{e}"))

