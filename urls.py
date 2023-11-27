from django.urls import path
from SE3 import views

urlpatterns = [
	path("login", views.login),
    path("Zeitbuchung", views.zeitbuchung),
    path("main", views.main),
    path("base_dir", views.getBaseDir),
    path("setcookie", views.SetCookie),         #   COOKIETEST
    path("getcookie", views.GetCookie)          #   COOKIETeST
    ]
