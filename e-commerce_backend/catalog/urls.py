from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryListView, ProductListView, ProductDetailView, ProductReviewView,
    CartView, CartAddView, CartUpdateItemView, CartClearView,
    OrderListView, OrderCreateView,
    SellerProductViewSet, ProductImageUploadView, SellerOrderView, VoucherPurchaseView, VoucherListView
)

router = DefaultRouter()
router.register('seller/products', SellerProductViewSet, basename='seller-products')

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="categories"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<slug:slug>/reviews/", ProductReviewView.as_view(), name="product-reviews"),

    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", CartAddView.as_view(), name="cart-add"),
    path("cart/update_item/", CartUpdateItemView.as_view(), name="cart-update-item"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),

    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/create/", OrderCreateView.as_view(), name="order-create"),

    # Seller
    path("", include(router.urls)),
    path("seller/upload-image/", ProductImageUploadView.as_view(), name="seller-upload-image"),
    path("seller/orders/", SellerOrderView.as_view(), name="seller-orders"),

    path('vouchers/purchase/', VoucherPurchaseView.as_view(), name='voucher-purchase'),
    path('vouchers/', VoucherListView.as_view(), name='voucher-list'),
]
