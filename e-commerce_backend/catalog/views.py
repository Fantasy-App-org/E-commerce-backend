import secrets
import string
import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics
from django.utils.text import slugify
from rest_framework.pagination import PageNumberPagination

from .models import Category, Product, ProductImage, Cart, CartItem, Order, OrderItem, Review, Voucher, PaymentTransaction, PlatformSettings
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductSerializer, ProductCreateSerializer, ProductImageSerializer,
    ReviewSerializer, CartSerializer, AddToCartSerializer,
    OrderSerializer, OrderItemSerializer, SellerProductSerializer, VoucherSerializer, VoucherPurchaseSerializer,
    PaymentTransactionSerializer, PaymentInitiateSerializer, PaymentCallbackSerializer
)

class StandardPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"

# ------------------ Category ------------------
class CategoryListView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# ------------------ Product ------------------
class ProductListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        queryset = Product.objects.filter(is_active=True).select_related("category", "seller").prefetch_related("images")
        category_slug = request.query_params.get("category__slug")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering", "-created_at")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search:
            queryset = queryset.filter(title__icontains=search)

        queryset = queryset.order_by(ordering)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        product = get_object_or_404(Product.objects.prefetch_related("images"), slug=slug, is_active=True)
        serializer = ProductDetailSerializer(product, context={"request": request})
        return Response(serializer.data)

# ------------------ Reviews ------------------
class ProductReviewView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        reviews = product.reviews.select_related("user")
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------ Cart ------------------
class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)

class CartAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data["product"]
            qty = serializer.validated_data["qty"]
            cart, _ = Cart.objects.get_or_create(user=request.user)
            item, created = CartItem.objects.get_or_create(
                cart=cart, product=product,
                defaults={"qty": qty, "price_snapshot": product.price}
            )
            if not created:
                item.qty += qty
                item.save()
            cart_serializer = CartSerializer(cart, context={"request": request})
            return Response(cart_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartUpdateItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        item_id = request.data.get("item_id")
        qty = int(request.data.get("qty", 1))
        try:
            item = CartItem.objects.get(pk=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=404)

        if qty <= 0:
            item.delete()
        else:
            if item.product.stock < qty:
                return Response({"detail": "Insufficient stock."}, status=400)
            item.qty = qty
            item.save()

        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)

class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."})

# ------------------ Orders ------------------
class OrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty."}, status=400)

        for it in cart.items.select_related("product"):
            if it.product.stock < it.qty:
                return Response({"detail": f"Insufficient stock for {it.product.title}."}, status=400)

        order = Order.objects.create(user=request.user)
        order_items = []
        for it in cart.items.select_related("product"):
            it.product.stock -= it.qty
            it.product.save(update_fields=["stock"])
            order_items.append(OrderItem(
                order=order, product=it.product,
                title_snapshot=it.product.title, price_snapshot=it.price_snapshot, qty=it.qty
            ))
        OrderItem.objects.bulk_create(order_items)
        
        # Calculate totals including GST and commission
        order.calculate_totals()
        
        cart.items.all().delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)

# ------------------ Seller Management ------------------
class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'seller_profile') and request.user.seller_profile.status == 'approved'

class SellerProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user).prefetch_related('images', 'category')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data['title']
        slug = slugify(title)
        sku = f"SKU-{get_random_string(8).upper()}"
        serializer.save(seller=self.request.user, slug=slug, sku=sku)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        product = serializer.instance
        # ✅ Return full product details after creation
        return Response(
            ProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        product = serializer.instance
        # ✅ Return full product details after update
        return Response(
            ProductSerializer(product, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response({"detail": "Product deactivated instead of deleting."}, status=status.HTTP_200_OK)


class ProductImageUploadView(APIView):
    permission_classes = [IsSeller]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        product = Product.objects.get(id=product_id, seller=request.user)

        files = request.FILES.getlist('images')  # ✅ Multiple images
        if not files:
            return Response({"detail": "No images uploaded"}, status=400)

        images = []
        for file in files:
            img = ProductImage.objects.create(product=product, image=file)
            images.append(ProductImageSerializer(img).data)

        return Response(images, status=201)


class SellerOrderView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return OrderItem.objects.filter(product__seller=self.request.user).select_related('order', 'product')


def generate_voucher_code(length=10):
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


class VoucherPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VoucherPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            value = serializer.validated_data['value']

            # Generate a unique voucher code
            while True:
                code = generate_voucher_code()
                if not Voucher.objects.filter(code=code).exists():
                    break

            voucher = Voucher.objects.create(
                code=code,
                value=value,
                user=request.user
            )
            return Response(VoucherSerializer(voucher).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoucherListView(generics.ListAPIView):
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Voucher.objects.filter(user=self.request.user).order_by('-created_at')


# ------------------ Payment Gateway ------------------
class PaymentInitiateView(APIView):
    """Initiate payment for an order"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            gateway = serializer.validated_data['payment_gateway']
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response({"detail": "Order not found."}, status=404)
            
            if order.payment_status == 'completed':
                return Response({"detail": "Order already paid."}, status=400)
            
            # Generate unique transaction ID
            transaction_id = f"{gateway.upper()}_{uuid.uuid4().hex[:12]}"
            
            # Create payment transaction record
            payment_transaction = PaymentTransaction.objects.create(
                order=order,
                transaction_id=transaction_id,
                payment_gateway=gateway,
                amount=order.total,
                status='initiated'
            )
            
            # Update order payment status
            order.payment_status = 'processing'
            order.payment_method = gateway
            order.payment_transaction_id = transaction_id
            order.save(update_fields=['payment_status', 'payment_method', 'payment_transaction_id'])
            
            # Here you would integrate with actual payment gateway
            # For now, return the transaction details for frontend to handle
            response_data = {
                'transaction_id': transaction_id,
                'order_id': order.id,
                'amount': float(order.total),
                'currency': 'INR',
                'gateway': gateway,
                'gateway_data': self._prepare_gateway_data(order, transaction_id, gateway)
            }
            
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)
    
    def _prepare_gateway_data(self, order, transaction_id, gateway):
        """Prepare gateway-specific data"""
        base_data = {
            'order_id': order.id,
            'amount': float(order.total),
            'currency': 'INR',
            'description': f'Order #{order.id}',
            'customer': {
                'name': order.user.name,
                'email': order.user.email,
                'phone': order.user.phone_number
            }
        }
        
        if gateway == 'razorpay':
            return {
                **base_data,
                'key': 'YOUR_RAZORPAY_KEY_ID',  # Replace with actual key
                'order_id': transaction_id,
                'callback_url': '/api/payment/callback/razorpay/',
                'prefill': base_data['customer']
            }
        elif gateway == 'payu':
            return {
                **base_data,
                'key': 'YOUR_PAYU_MERCHANT_KEY',  # Replace with actual key
                'txnid': transaction_id,
                'surl': '/api/payment/callback/payu/success/',
                'furl': '/api/payment/callback/payu/failure/',
                'productinfo': base_data['description']
            }
        
        return base_data


class PaymentCallbackView(APIView):
    """Handle payment gateway callbacks"""
    permission_classes = [permissions.AllowAny]  # Gateway callbacks don't have user auth

    def post(self, request, gateway):
        """Handle payment callback from gateway"""
        if gateway not in ['razorpay', 'payu', 'stripe', 'paypal']:
            return Response({"detail": "Invalid gateway."}, status=400)
        
        # Extract transaction ID from request data
        transaction_id = request.data.get('transaction_id') or request.data.get('txnid')
        
        if not transaction_id:
            return Response({"detail": "Transaction ID missing."}, status=400)
        
        try:
            payment_transaction = PaymentTransaction.objects.get(transaction_id=transaction_id)
            order = payment_transaction.order
        except PaymentTransaction.DoesNotExist:
            return Response({"detail": "Transaction not found."}, status=404)
        
        # Process gateway-specific response
        success = self._process_gateway_response(gateway, request.data, payment_transaction)
        
        if success:
            payment_transaction.status = 'success'
            order.payment_status = 'completed'
            order.status = 'paid'
        else:
            payment_transaction.status = 'failed'
            order.payment_status = 'failed'
        
        payment_transaction.gateway_response = request.data
        payment_transaction.save()
        order.save(update_fields=['payment_status', 'status'])
        
        return Response({
            'status': 'success' if success else 'failed',
            'order_id': order.id,
            'transaction_id': transaction_id
        })
    
    def _process_gateway_response(self, gateway, data, payment_transaction):
        """Process gateway-specific response data"""
        if gateway == 'razorpay':
            # Verify Razorpay signature here
            return data.get('status') == 'success'
        elif gateway == 'payu':
            # Verify PayU hash here
            return data.get('status') == 'success'
        elif gateway == 'stripe':
            # Verify Stripe webhook signature here
            return data.get('status') == 'succeeded'
        
        return False


class PaymentStatusView(APIView):
    """Check payment status for an order"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            transactions = order.payment_transactions.all().order_by('-created_at')
            
            return Response({
                'order_id': order.id,
                'payment_status': order.payment_status,
                'order_status': order.status,
                'total_amount': order.total,
                'transactions': PaymentTransactionSerializer(transactions, many=True).data
            })
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)


def generate_voucher_code(length=10):
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))