# from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from api_auth.models import CustomUser, SocialAccount
from api_auth.serializers import UserSerializer, TokenClaimObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status

# from rest_framework.metadata import SimpleMetadata
# from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
# from rest_framework.permissions import IsAuthenticated
# from api_auth.custom_meta_data_class import CustomMetadata
# import jsonschema
# from jsonschema import ValidationError
from api_auth.schemas import CustomJSONParser, CustomJSONRenderer
from api_auth.metadata import METADATA_CHECK_EMAIL
from rest_framework.decorators import action
from rest_framework import serializers
from django.core.cache import cache
from datetime import timedelta


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenClaimObtainPairSerializer


class UserCreateView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    parser_classes = [CustomJSONParser]
    # renderer_classes = [CustomJSONRenderer]

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
    metadata_class = METADATA_CHECK_EMAIL

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
        cache.set(cache_key, result, timeout=timedelta(days=1))

        if existing_social_user and existing_user:
            return Response({"exists": True, "email": email}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"exists": False, "email": email}, status=status.HTTP_404_NOT_FOUND
            )


# class SignupView(View):
#     template_name = "signup.html"
#     form_class = SignUpForm

#     def get(self, request):
#         form = self.form_class()
#         return render(request, self.template_name, {"form": form})

#     def post(self, request):
#         email = request.POST.get(
#             "email"
#         )  # Assuming the email comes from the form POST data

#         existing_social_user = SocialAccount.objects.select_related(
#             user_info__icontains=email
#         ).exists()
#         # Check if the user with the email already exists
#         existing_user = CustomUser.objects.select_related(email=email).exists()

#         if existing_social_user or existing_user:
#             messages.error(request, "A user with the email already exists")
#             return redirect("Homepage:signup")
#         else:
#             form = self.form_class(request.POST)
#             if form.is_valid():
#                 user = form.save()
#                 if user is not None:
#                     messages.success(request, "your account is created, Please login!")
#                     return redirect("Homepage:login")
#             else:
#                 for field, errors in form.errors.items():
#                     for error in errors:
#                         messages.error(request, f"{field}: {error}")

#         return render(request, self.template_name, {"form": form})
