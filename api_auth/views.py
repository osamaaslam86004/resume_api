from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from api_auth.models import CustomUser, UserProfile, CustomerProfile, SocialAccount
from api_auth.serializers import (
    TokenClaimObtainPairSerializer,
    UserSerializer,
    CustomUserSerializer,
    UserProfileSerializer,
    CustomerProfileSerializer,
    CustomUserImageSerializer,
)
from api_auth.permissions import HasCustomerProfilePermission
from rest_framework.permissions import IsAuthenticated
from api_auth.fields import UIDB64TokenField
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from api_auth.schemas import CustomJSONParser, CustomJSONRenderer
from api_auth.metadata import METADATA_JSON_PARSES_JSON_RENDERS, PasswordResetMetadata
from rest_framework.decorators import action
from rest_framework import serializers
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
import json, requests
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from api_auth.authentication import CSRFTrustedOriginAuthentication
from rest_framework.exceptions import ParseError
from django.db import transaction


import cloudinary

if not settings.DEBUG:
    cloudinary.config(
        cloud_name="dh8vfw5u0",
        api_key="667912285456865",
        api_secret="QaF0OnEY-W1v2GufFKdOjo3KQm8",
        api_proxy="http://proxy.server:3128",
    )
else:
    cloudinary.config(
        cloud_name="dh8vfw5u0",
        api_key="667912285456865",
        api_secret="QaF0OnEY-W1v2GufFKdOjo3KQm8",
    )
import cloudinary.uploader
from cloudinary.uploader import upload


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


class UserCreateView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    allowed_methods = ["POST", "GET"]
    serializer_class = UserSerializer
    authentication_classes = [CSRFTrustedOriginAuthentication]
    parser_classes = [CustomJSONParser]

    def list(self, request, *args, **kwargs):
        return Response(data={"error": "Method not allowed"})

    @action(detail=False, methods=["GET"])
    def get_api_user_id_for_user(self, request, *args, **kwargs):

        if (
            "username" in request.data
            and "email" in request.data
            and "password" in request.data
            and request.data["username"]
            and request.data["email"]
            and request.data["password"] is not None
        ):
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")

            print(username)
            print(email)
            print(password)

            try:
                queryset = CustomUser.objects.get_user(email, username, password)
                if queryset:
                    serializer = self.get_serializer(queryset)
                    return Response(serializer.data)
                else:
                    return Response(
                        {"error": "User does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            except Exception as e:
                return Response({"error": str(e)})
        else:
            return Response(
                {
                    "keys": "one of the keys is missing from list [username, password, username]",
                    "values": "either email is None or password is None",
                }
            )


class CheckEmailExistence(APIView):
    allowed_methods = ["POST"]
    metadata_class = METADATA_JSON_PARSES_JSON_RENDERS

    class EmailSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request, *args, **kwargs):
        serializer = self.EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")

        # Check if the result is cached
        cache_key = f"email_existence_{email}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result, status=status.HTTP_200_OK)

        existing_social_user = SocialAccount.objects.filter(
            user_info__icontains=email
        ).exists()
        # Check if the user with the email already exists
        existing_user = CustomUser.objects.filter(email=email).exists()

        # Cache the results
        result = {"exists": existing_social_user and existing_user, "email": email}
        cache.set(cache_key, result)

        if existing_social_user and existing_user:
            return Response(
                {"exists": "True", "email": email}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"exists": "False", "email": email}, status=status.HTTP_404_NOT_FOUND
            )


class CustomLoginAPIView(APIView):
    allowed_methods = ["POST", "GET"]
    metadata_class = METADATA_JSON_PARSES_JSON_RENDERS

    class InputOutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request):
        serializer = self.InputOutputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        user = authenticate(
            request=request,
            email=email,
            password=password,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        if user is not None:
            login(request, user)
            user = self.InputOutputSerializer(request.data).data
            request.session["user_id"] = CustomUser.objects.filter(email=email)[0].id
            return Response({"user": user}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    def get(self, request):

        if "user_id" in request.session:
            user_id = request.session.get("user_id")
            user = authenticate(request=request, user_id=user_id)
            if user is not None:
                login(
                    request,
                    user,
                    backend="django.contrib.auth.backends.ModelBackend",
                )

                return Response({"user": user}, status=status.HTTP_200_OK)
            else:
                return Response({"user": user}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"session": request.session}, status=status.HTTP_404_NOT_FOUND
            )


class CustomLogoutView(APIView):
    allowed_methods = ["GET"]

    def get(self, request):
        if "user_id" in request.session:
            user_id = request.session["user_id"]
            print(f"user_id___________________{user_id}")
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class IsAuthenticatedCheck(APIView):
    allowed_methods = ["GET"]

    def get(self, request):
        if request.session and "user_id" in request.session:
            user_id = request.session["user_id"]
            user_authenticated = CustomUser.objects.filter(id=user_id)[
                0
            ].is_authenticated
            if user_authenticated:
                return Response(
                    {"user_authenticated": user_authenticated},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"user_authenticated": user_authenticated},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        elif request.user.is_authenticated:
            return Response(
                {"is_authenticated": request.user.is_authenticated},
                status=status.HTTP_200_OK,
            )
        elif not request.user.is_authenticated:
            return Response(
                {"is_authenticated": request.user.is_authenticated},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"session not found": "session not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomPasswordReset(APIView):
    allowed_methods = ["POST"]
    metadata_class = METADATA_JSON_PARSES_JSON_RENDERS

    class EmailSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request):
        serializer = self.InputOutputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")

        user = CustomUser.objects.filter(email=email)[0]

        if user is not None:
            try:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_url = request.build_absolute_uri(
                    reverse(
                        "Homepage:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )

                # Define the SendGrid API endpoint
                SENDGRID_API_ENDPOINT = "https://api.sendgrid.com/v3/mail/send"

                # Define your SendGrid API key
                SENDGRID_API_KEY = settings.SENDGRID_API_KEY

                # Define the email message
                message = {
                    "personalizations": [
                        {"to": [{"email": email}], "subject": "Reset your password"}
                    ],
                    "from": {"email": settings.CLIENT_EMAIL},
                    "content": [
                        {
                            "type": "text/html",
                            "value": f'Click the link to reset your password: <a href="{reset_url}">{reset_url}</a>',
                        }
                    ],
                }
                # Convert the message to JSON format
                message_json = json.dumps(message)

                # Set the headers with the API key
                headers = {
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json",
                }

                # Send the email using the requests library
                response = requests.post(
                    SENDGRID_API_ENDPOINT,
                    headers=headers,
                    data=message_json,
                    verify=False,
                )

                print(response.status_code)
                print(response.content)

                if response.status_code == 202:
                    return Response({"status": "ok"}, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"status": "failed"}, status=status.HTTP_400_BAD_REQUEST
                    )

            except requests.exceptions.RequestException as e:
                return Response(
                    {"message": f"Error: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"user not found": email}, status=status.HTTP_400_BAD_REQUEST
            )


class GetCustomPasswordResetConfirmView(APIView):
    allowed_methods = ["GET"]
    metadata_class = PasswordResetMetadata
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    class InputSerializer(serializers.Serializer):
        uidb64 = UIDB64TokenField()
        token = UIDB64TokenField()

    def get(self, request):

        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": status.HTTP_200_OK})


class PostCustomPasswordResetConfirmView(APIView):
    allowed_methods = ["POST"]
    metadata_class = PasswordResetMetadata
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    class OutputSerializer(serializers.Serializer):
        uidb64 = UIDB64TokenField()
        token = UIDB64TokenField()
        password = serializers.CharField()

    def post(self, request):

        serializer = self.OutputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            password = serializer.validated_data["password"]
            user = serializer.validated_data["user"]
            user.set_password(password)
            user.save()
            return Response({"status": status.HTTP_200_OK})


class GetCustomerProfilePageAPIView(APIView):
    permission_required = [
        "api_auth.customer_create_profile",
        "api_auth.customer_edit_profile",
        "api_auth.customer_delete_profile",
    ]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, HasCustomerProfilePermission]
    allowed_methods = ["GET"]
    serializer_class = [
        UserProfileSerializer,
        CustomerProfileSerializer,
        CustomUserImageSerializer,
    ]

    def get(self, request):
        # Fetch user data
        user = request.user
        user = CustomUser.objects.get(pk=request.user.id)

        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=user
        )

        customer_profile, created_customer_profile = (
            CustomerProfile.objects.get_or_create(
                customer_profile=user_profile, customuser_type_1=user
            )
        )

        # Deserialize request data
        user_profile_serializer = self.serializer_class[0](instance=user_profile).data
        customer_profile_serializer = self.serializer_class[1](
            instance=customer_profile
        ).data
        custom_user_image_serializer = self.serializer_class[2](
            instance=request.user
        ).data

        return Response(
            {
                "image": custom_user_image_serializer,
                "user_profile": user_profile_serializer,
                "customer_profile": customer_profile_serializer,
                "permissions": [
                    Permissions.split(".")[1]
                    for Permissions in user.get_all_permissions()
                ],
            },
            status=status.HTTP_200_OK,
        )


class CreateCustomerProfilePageAPIView(APIView):
    permission_required = [
        "api_auth.customer_create_profile",
        "api_auth.customer_edit_profile",
        "api_auth.customer_delete_profile",
    ]
    allowed_methods = ["POST"]
    serializer_class = [
        UserProfileSerializer,
        CustomerProfileSerializer,
        CustomUserImageSerializer,
    ]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, HasCustomerProfilePermission]

    def post(self, request):
        # Fetch user data
        user = request.user
        user = CustomUser.objects.get(pk=request.user.id)

        user_profile, created_user_profile = UserProfile.objects.get_or_create(
            user=user
        )

        customer_profile, created_customer_profile = (
            CustomerProfile.objects.get_or_create(
                customer_profile=user_profile, customuser_type_1=user
            )
        )

        transformation_options = {
            "width": 75,
            "height": 75,
            "crop": "fill",
            "gravity": "face",
            "effect": "auto_contrast",
        }
        try:
            with transaction.atomic():
                image_data = upload(
                    file=request.FILES["image"],
                    transformation=transformation_options,
                    resource_type="image",
                )

                self.request.user.image = image_data["url"]
                self.request.user.save()

            user_profile_serializer = self.serializer_class[0](
                instance=user_profile, data=request.data.get("user_profile")
            )
            customer_profile_serializer = self.serializer_class[1](
                instance=customer_profile,
                data=request.data.get("customer_profile"),
            )
            custom_user_image_serializer = self.serializer_class[2](
                instance=user, data=request.data.get("custom_user_image"), partial=True
            )

            # Validate and save data
            user_profile_valid = user_profile_serializer.is_valid()
            customer_profile_valid = customer_profile_serializer.is_valid()
            custom_user_image_valid = custom_user_image_serializer.is_valid()

            if (
                user_profile_serializer.is_valid()
                and customer_profile_serializer.is_valid()
                and custom_user_image_serializer.is_valid()
            ):
                user_profile_serializer.save()
                customer_profile_serializer.save()
                custom_user_image_serializer.save()
                return Response(
                    {"message": "Profile updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                errors = {
                    **user_profile_serializer.errors,
                    **customer_profile_serializer.errors,
                    **custom_user_image_serializer.errors,
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
