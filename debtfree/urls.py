from django.urls import path
from . import views

urlpatterns = [
    path("sw.js",                 views.service_worker, name="sw"),
    path("",                      views.home,        name="home"),
    path("login/",                views.login_view,  name="login"),
    path("logout/",               views.logout_view, name="logout"),
    path("onboarding/",           views.onboarding,  name="onboarding"),
    path("analyze/",              views.analyze,     name="analyze"),

    path("renda/",                views.renda,        name="renda"),

    path("perfil/",               views.perfil,    name="perfil"),

    # Tadeu — resultados e ação
    path("dashboard/",                        views.dashboard, name="dashboard"),
    path("dashboard/legal/",                  views.legal,     name="legal"),
    path("dashboard/letter/<int:debt_index>/", views.letter,   name="letter"),
]
