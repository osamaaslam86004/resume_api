from rest_framework import serializers
from api_auth.models import CustomUser, UserProfile, CustomerProfile
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from django_countries.serializers import CountryFieldMixin


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        # is_staff, is_active fields will used in serializing(Get user), and not in de-serializing (create/update user)
        # fields = ["id", 'email', 'username', 'password', "is_staff", "is_active",
        #           "locality", "facebook"]
        fields = [
            "id",
            "email",
            "username",
            "password1",
            "password2",
            "user_type",
            "is_staff",
            "is_active",
        ]

    def create(self, validated_data):
        if validated_data["password1"] == validated_data["password2"]:

            user = CustomUser.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password1"],
                username=validated_data["username"],
                user_type=validated_data["user_type"],
            )
            return user
        else:
            raise ValidationError("Passwords do not match.")


class TokenClaimObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user"] = user.username

        return token


class CustomUserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["image"]


class UserProfileSerializer(serializers.ModelSerializer, CountryFieldMixin):
    phone_number = PhoneNumberField()

    class Meta:
        model = UserProfile
        fields = [
            "full_name",
            "age",
            "gender",
            "phone_number",
            "city",
            "country",
            "postal_code",
            "shipping_address",
        ]


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = "__all__"


class CustomUserSerializer(serializers.ModelSerializer):
    # user_profile = UserProfileSerializer()
    # customer_profile = CustomerProfileSerializer()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "image",
            # "user_profile",
            # "customer_profile",
        ]
        depth = 1
