from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import SellerProfile
from .models import Category, Product, ProductImage, Review, Cart, CartItem, Order, OrderItem, Voucher


# ------------------ Category ------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']  # slug will be auto-generated
# ------------------ Product ------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt"]

    def get_image(self, obj):
        request = self.context.get("request", None)
        if not obj.image:
            return None
        url = obj.image.url
        if request:
            return request.build_absolute_uri(url)
        return url

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "title", "slug", "price", "mrp", "brand", "stock", "category", "thumbnail"]

    def get_thumbnail(self, obj):
        img = obj.images.first()
        return self.context["request"].build_absolute_uri(img.image.url) if img else None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "title", "slug", "description", "price", "mrp", "brand", "sku", "stock",
                  "category", "images", "is_active", "created_at"]

# ✅ Missing ProductSerializer (Generic)
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

# ------------------ Reviews ------------------
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "user_name", "rating", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

# ------------------ Seller Management ------------------
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "title", "description", "price", "mrp", "stock", "is_active", "brand", "sku", "category"
        ]

class SellerProductSerializer(serializers.ModelSerializer):
    # Change this line to use CategorySerializer
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "title", "slug", "description", "price", "mrp", "stock", "is_active",
            "brand", "sku", "category", "images", "created_at"
        ]

class SellerOrderItemSerializer(serializers.ModelSerializer):
    buyer = serializers.CharField(source="order.user.name", read_only=True)
    order_status = serializers.CharField(source="order.status", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "title_snapshot", "price_snapshot", "qty",
            "subtotal", "buyer", "order_status"
        ]

# ------------------ Cart ------------------
class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    image = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_title", "qty", "price_snapshot", "subtotal", "image"]

    def get_image(self, obj):
        img = obj.product.images.first()
        request = self.context.get("request")
        return request.build_absolute_uri(img.image.url) if (request and img) else None

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "updated_at"]

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)

    def validate(self, data):
        from .models import Product
        try:
            product = Product.objects.get(pk=data["product_id"], is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        if product.stock < data["qty"]:
            raise serializers.ValidationError("Insufficient stock.")
        data["product"] = product
        return data

# ------------------ Orders ------------------
class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "title_snapshot", "price_snapshot", "qty", "subtotal"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "items", "created_at", "shipped_at"]



class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ['id', 'code', 'value', 'is_used']

class VoucherPurchaseSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=10, decimal_places=2)
