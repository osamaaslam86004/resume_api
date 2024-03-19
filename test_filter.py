import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resume_api.settings")

import django

django.setup()


import random
import string
from django.contrib.auth import get_user_model
from django.utils import timezone
from api_auth.models import SocialAccount


UserModel = get_user_model()


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def populate_social_accounts(num_accounts):
    for _ in range(num_accounts):
        user = UserModel.objects.create(
            username=generate_random_string(10),
            email=f"{generate_random_string(8)}@example.com",
            user_type=random.choice(
                [
                    "CUSTOMER",
                    "SELLER",
                    "CUSTOMER REPRESENTATIVE",
                    "MANAGER",
                    "ADMINISTRATOR",
                ]
            ),
        )
        SocialAccount.objects.create(
            user=user,
            access_token=generate_random_string(100),
            user_info=f"username = {user.username} email = {user.email}",
            token_created_at=timezone.now(),
            code=generate_random_string(50),
            refresh_token=generate_random_string(100),
        )


num_social_accounts = 500
num_custom_users = 500
populate_social_accounts(num_social_accounts)
