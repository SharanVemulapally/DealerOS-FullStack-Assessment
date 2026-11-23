from django.urls import path
from reconcile.views import disagreements
urlpatterns = [path("api/disagreements/", disagreements, name="disagreements")]
