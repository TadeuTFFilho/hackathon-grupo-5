def current_user(request):
    """Disponibiliza o usuário logado em todos os templates via {{ current_user }}."""
    return {"current_user": request.session.get("user")}
