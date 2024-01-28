from django.urls import path
from SE3 import views

urlpatterns = [
	path("login/", views.login),
    path("Zeitbuchung", views.zeitbuchung),
    path("main", views.main),
    path("logout/", views.logout),
    path("base_dir", views.getBaseDir),
    path("personenTest", views.personenTest),
    path("signieren", views.signieren),
    #path("setcookie", views.SetCookie),         #   COOKIETEST
    #path("getcookie", views.GetCookie),          #   COOKIETeST
    ]
