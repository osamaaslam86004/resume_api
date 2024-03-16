from django.conf import settings
from i.your_browsing_history import your_browsing_history
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

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


class HomePageView(APIView):

    def get(self, request, **kwargs):
        data = request.data
        if "images" in data and "cart_icon" in data and images is not [] and cart_icon:

            images = data["images"]
            cart_icon = data["cart_icon"]

            image_urls = [
                cloudinary.CloudinaryImage(name).build_url() for name in images
            ]
            cart_url = cloudinary.CloudinaryImage(cart_icon).build_url()
            zipped = your_browsing_history(self.request)

            data["images"] = image_urls
            data["cart_url"] = cart_url
            data["zipped"] = zipped

            return Response({"data": data}, status=status.HTTP_200_OK)
