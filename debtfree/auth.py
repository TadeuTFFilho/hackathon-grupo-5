"""
Helpers de autenticação mockada.
Substituir por autenticação real quando Luis integrar o backend.
"""
from functools import wraps
from django.shortcuts import redirect


def login_required(view_func):
    """Redireciona para /login/ se o usuário não estiver autenticado."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("user"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
