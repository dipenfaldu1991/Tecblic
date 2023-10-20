from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, ChangePasswordSerializer, ForgotPasswordSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model
from .utils import generate_otp, send_otp_email,send_forgot_password_email
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import UserProfile
from .exceptions import Conflict, AlreadyExists
from .permissions import IsAdminUser, IsproviderUser, IsseekerUser

"""set user model using setting.py file"""
User = get_user_model()

class UserRegistrationView(APIView):
    """user register post method for user create new user. """
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': 'User register successfully'
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""login api for user login with otp"""

class LoginWithOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()
        user.otp = otp
        user.save()

        # send_otp_email(email, otp)
        # send_otp_phone(phone_number, otp)

        return Response({'message': 'OTP has been sent to your email.'}, status=status.HTTP_200_OK)

"""Login otp verification"""
class ValidateOTP(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        otp = request.data.get('otp', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == str(otp):
            user.otp = None  # Reset the OTP field after successful validation
            user.save()

            # Authenticate the user and create or get an authentication token
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

"""login user password change api"""
class ChangePasswordView(APIView):
    permission_classes = [IsAdminUser| IsproviderUser| IsseekerUser,]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']

            if not user.check_password(old_password):
                return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(new_password) == user.check_password(old_password):
                return Response({'detail': 'Old password and New password are same please change New password.'}, status=status.HTTP_400_BAD_REQUEST)
            if new_password != confirm_password:
                return Response({'detail': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""Forgot password api"""
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'No user with this email address.'}, status=status.HTTP_404_NOT_FOUND)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f'https://your-frontend-url/reset-password/{uid}/{token}/'

            # Send the reset link to the user's email
            send_forgot_password_email(reset_link,email)

            return Response({'detail': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"User profile api"
class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser| IsproviderUser| IsseekerUser,]
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


    def perform_create(self, serializer):
        if UserProfile.objects.filter(user=self.request.user):
            raise AlreadyExists('User profile already exist,')
        # Associate the profile with the currently logged-in user
        serializer.save(user=self.request.user)


    def update(self, request, *args, **kwargs):
        # update api for current user profile
        instance = self.get_object()
        if instance.user == self.request.user:
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            raise Conflict('Request conflicts with the current user profile of the server.')

