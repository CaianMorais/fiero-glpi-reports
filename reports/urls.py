from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("chamados-por-area/", views.chamados_por_area, name="chamados_por_area"),
    path("media_satisfacao/", views.media_satisfacao, name="media_satisfacao"),
    path("chamados-por-area/export.csv", views.chamados_por_area_csv, name="chamados_por_area_csv"),
    path("media_satisfacao/export.csv", views.media_satisfacao_csv, name="media_satisfacao_csv"),
]