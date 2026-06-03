from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("idioma/<str:lang>/", views.set_language, name="set_language"),
    path("healthz/", views.health, name="health"),
    path("robots.txt", views.robots, name="robots"),
]
