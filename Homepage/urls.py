from django.urls import path
from Homepage.views import HomePageView


urlpatterns = [
    path(
        "",
        HomePageView.as_view(),
    ),
]
