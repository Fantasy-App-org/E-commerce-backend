from django.contrib import admin
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, PlatformSettings, PaymentTransaction

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'brand', 'sku')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'gst_rate')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('gst_rate',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'subtotal', 'gst_amount', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    readonly_fields = ('subtotal', 'gst_amount', 'commission_amount', 'total')

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('commission_rate', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not PlatformSettings.objects.exists()

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'payment_gateway', 'amount', 'status', 'created_at')
    list_filter = ('payment_gateway', 'status', 'created_at')
    readonly_fields = ('transaction_id', 'gateway_response', 'created_at', 'updated_at')
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
