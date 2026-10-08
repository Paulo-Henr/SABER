from functools import wraps
 
from flask import flash, redirect, url_for
from flask_login import current_user
 
from extensions import login_manager
 
 
def admin_required(view_func):
    @wraps(view_func)
    def rota_protegida(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.is_admin:
            flash("Acesso restrito a administradores.", "erro")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)
 
    return rota_protegida