from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("pages/about/", views.AboutView.as_view(), name="about"),
    path("pages/rules/", views.RulesView.as_view(), name="rules"),
]
