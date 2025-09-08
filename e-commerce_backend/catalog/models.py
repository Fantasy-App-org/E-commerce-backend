from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal
import json

# --- Core catalog models ---

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    gst_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00,
        help_text="GST rate in percentage"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def gst_rate_decimal(self):
        """Return GST rate as decimal (18% = 0.18)"""
        return self.gst_rate / 100
class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # optional simple attributes
    brand = models.CharField(max_length=120, blank=True)
    sku = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title

    @property
    def price_with_gst(self):
        """Calculate price including GST"""
        gst_amount = self.price * self.category.gst_rate_decimal
        return self.price + gst_amount

    @property
    def gst_amount(self):
        """Calculate GST amount for this product"""
        return self.price * self.category.gst_rate_decimal
    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt = models.CharField(max_length=200, blank=True)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")


# --- Cart / Order ---

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot current price

    class Meta:
        unique_together = ("cart", "product")

    @property
    def subtotal(self):
        return self.qty * self.price_snapshot

    @property
    def gst_amount(self):
        """Calculate GST amount for this cart item"""
        gst_rate = self.product.category.gst_rate / 100
        return self.subtotal * gst_rate

    @property
    def total_with_gst(self):
        """Calculate total including GST"""
        return self.subtotal + self.gst_amount


class Order(models.Model):
    STATUS = (
        ("created", "Created"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS, default="created")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Payment fields
    PAYMENT_STATUS = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    def calculate_totals(self):
        """Calculate subtotal, GST, commission and total"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.gst_amount = sum(item.gst_amount for item in self.items.all())
        
        # Calculate platform commission
        try:
            settings = PlatformSettings.objects.first()
            commission_rate = settings.commission_rate / 100 if settings else Decimal('0.05')
        except:
            commission_rate = Decimal('0.05')  # Default 5%
        
        self.commission_amount = self.subtotal * commission_rate
        self.total = self.subtotal + self.gst_amount
        self.save(update_fields=['subtotal', 'gst_amount', 'commission_amount', 'total'])

    def __str__(self):
        return f"Order#{self.pk} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    title_snapshot = models.CharField(max_length=200)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.qty * self.price_snapshot

    @property
    def gst_amount(self):
        """Calculate GST amount for this order item"""
        gst_rate = self.product.category.gst_rate / 100
        return self.subtotal * gst_rate


class PlatformSettings(models.Model):
    """Platform configuration settings"""
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=5.00,
        help_text="Platform commission rate in percentage"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"

    def __str__(self):
        return f"Commission Rate: {self.commission_rate}%"


class PaymentTransaction(models.Model):
    """Payment transaction records"""
    GATEWAY_CHOICES = (
        ('razorpay', 'Razorpay'),
        ('payu', 'PayU'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    )
    
    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_transactions')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"

class Voucher(models.Model):
    code = models.CharField(max_length=20, unique=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Voucher {self.code} ({self.value})"
