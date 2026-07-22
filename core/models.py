from django.db import models
import random

class Product(models.Model):
    name = models.CharField(max_length=200)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class POSUser(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('attendant', 'Attendant'),
        ('cashier', 'Cashier'),
        ('dispatcher', 'Dispatcher'),
    ]
    name = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    pin = models.CharField(max_length=128) # Stores hashed PIN

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('dispatched', 'Dispatched'),
    ]

    customer_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    token = models.CharField(max_length=3, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Tracking accountability
    created_by = models.ForeignKey(POSUser, related_name='created_orders', on_delete=models.SET_NULL, null=True, blank=True)
    processed_by = models.ForeignKey(POSUser, related_name='processed_orders', on_delete=models.SET_NULL, null=True, blank=True)
    dispatched_by = models.ForeignKey(POSUser, related_name='dispatched_orders', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

    def generate_token(self):
        if not self.token:
            # Generate a random 3-digit token
            self.token = f"{random.randint(0, 999):03d}"
            self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Cost at time of order
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

    @property
    def total_price(self):
        return self.quantity * self.unit_price

class ActivityLog(models.Model):
    user = models.ForeignKey(POSUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name if self.user else 'System'} - {self.action} at {self.timestamp}"
