from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from api_auth.views import (
    UserCreateView,
    MyTokenObtainPairView,
    CheckEmailExistence,
    CustomLoginAPIView,
    CustomLogoutView,
    IsAuthenticatedCheck,
    CustomPasswordReset,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

router = DefaultRouter()
router.register(r"crud-user", UserCreateView, basename="crud-user")


urlpatterns = [
    # get the access token
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # provide user details with refresh token to get new access token
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "get-api-user-id-for-user/",
        UserCreateView.as_view({"get": "get_api_user_id_for_user"}),
        name="get_api_user_id_for_user",
    ),
    # check if email is unique
    path("check-email/", CheckEmailExistence.as_view(), name="check_email_existence"),
    path("login/", CustomLoginAPIView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("is-authenticated/", IsAuthenticatedCheck.as_view(), name="is-authenticated"),
    path(
        "custom-password-reset/", CustomPasswordReset.as_view(), name="password-reset"
    ),
] + [path("", include(router.urls))]
