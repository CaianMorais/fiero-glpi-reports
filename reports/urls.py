from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("chamados-por-area/", views.chamados_por_area, name="chamados_por_area"),
    path("chamados-por-area/export.csv", views.chamados_por_area_csv, name="chamados_por_area_csv"),
]