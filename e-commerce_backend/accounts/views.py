from rest_framework import generics, status, permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Notification
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, NotificationSerializer, \
    SellerProfileSerializer, ProfileSerializer

from .models import SellerProfile

@api_view(['PATCH'])
@permission_classes([IsAdminUser])  # Only admin can approve
def approve_seller(request, seller_id):
    try:
        seller = SellerProfile.objects.get(id=seller_id)
        seller.status = "approved"
        seller.save()
        return Response({"detail": "Seller approved successfully."})
    except SellerProfile.DoesNotExist:
        return Response({"detail": "Seller not found."}, status=404)


class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)






class HomeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "sections": [
                "Notifications",
                "Home Navigation Bar",
                "Profile Page",
                "About Section",
                "Seller Registration"
            ],
            "feature_flags": {
                "wallet": False,   # disabled for now
                "booking": False   # disabled for now
            }
        })





class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class SellerRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "seller_profile", None)
        if not profile:
            return Response({"exists": False, "status": None})
        data = SellerProfileSerializer(profile).data
        data.update({"exists": True})
        return Response(data)

    def post(self, request):
        serializer = SellerProfileSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(SellerProfileSerializer(profile).data, status=201)

class NotificationsListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        n.is_read = True
        n.save()
        return Response({"ok": True})

class AboutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "app": "Inway Shopy",
            "version": "0.1.0",
            "about": "Inway Shopy is an e-commerce platform for FMCG, Electronics and Fashion. Wallet & booking features are coming soon.",
            "contact_email": "support@inwayshopy.local"
        })