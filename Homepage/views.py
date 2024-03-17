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
        api_proxy = "http://proxy.server:3128"
    )
import cloudinary.uploader
from cloudinary.uploader import upload


class HomePageView(APIView):
    http_method_names = ['post', 'options']

    def post(self, request, **kwargs):
        data = request.data
        print(data)

        images = data.get("images", [])  # Initialize with an empty list
        cart_icon = data.get("cart_icon")

        if images and cart_icon:
            try:
                image_urls = [
                    cloudinary.CloudinaryImage(name).build_url() for name in images
                ]
                cart_url = cloudinary.CloudinaryImage(cart_icon).build_url()
                print(image_urls)

                zipped = your_browsing_history(self.request)

                data = {}
                data["images"] = image_urls
                data["cart_url"] = cart_url
                data["zipped"] = zipped
            except Exception as e:
                return Response({"error": str(e)})
            return Response({"data": data}, status=status.HTTP_200_OK)
