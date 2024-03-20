from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import ValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator


class UIDB64TokenField(serializers.Field):
    def to_internal_value(self, data):
        try:
            # Decode uidb64 and check if it's a valid base64 string
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
        except (TypeError, ValueError, OverflowError):
            raise ValidationError("Invalid uidb64")

        try:
            # Check if the user exists
            user = CustomUser.objects.get(pk=uid)
        except CustomUser.DoesNotExist:
            raise ValidationError("User does not exist")

        if "token" in data and data["token"]:
            if not default_token_generator.check_token(user, data["token"]):
                raise ValidationError("Invalid token")

        # Return the validated data
        data["user"] = user
        return data
