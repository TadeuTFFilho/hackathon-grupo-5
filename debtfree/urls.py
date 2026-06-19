from django.urls import path
from . import views

urlpatterns = [
    path("",                      views.home,      name="home"),
    path("onboarding/",           views.onboarding, name="onboarding"),
    path("analyze/",              views.analyze,   name="analyze"),

    # Tadeu — resultados e ação
    path("dashboard/",            views.dashboard, name="dashboard"),
    path("dashboard/legal/",      views.legal,     name="legal"),
    path("dashboard/letter/<int:debt_index>/", views.letter, name="letter"),
]
