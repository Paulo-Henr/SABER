from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
import models
import seed
from extensions import db, login_manager
from decorators import admin_required
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

models.criar_banco_se_nao_existir()

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()
    seed.popular_dados_exemplo()

@login_manager.user_loader
def carregar_usuario(identificador):
    return models.carregar_conta(identificador)

def destino_seguro(destino):
    #Só aceita redirecionar para caminhos DESTE site (ex.: /admin), recusando qualquer outro
    return (
        bool(destino)
        and destino.startswith("/")
        and not destino.startswith("//")
        and "\\" not in destino
    )

@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("entrar"))
    if current_user.is_admin:
        return redirect(url_for("admin_painel"))
    return redirect(url_for("catalogo"))

@app.route("/entrar", methods=["GET", "POST"])
def entrar():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
 
    proxima = request.form.get("next") or request.args.get("next") or ""
 
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
 
        if not email or not senha:
            flash("Informe e-mail e senha.", "erro")
            return render_template("entrar.html", email=email, proxima=proxima)
 
        conta = models.buscar_conta_por_email(email)
 
        if conta is None or not conta.verificar_senha(senha):
            flash("E-mail ou senha inválidos.", "erro")
            return render_template("entrar.html", email=email, proxima=proxima)
 
        login_user(conta)
        if destino_seguro(proxima):
            return redirect(proxima)
        return redirect(url_for("index"))
 
    return render_template("entrar.html", email="", proxima=proxima)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash("Sessão encerrada.", "sucesso")
    return redirect(url_for("entrar"))

@app.route("/admin")
@admin_required
def admin_painel():
    total_usuarios = models.Usuario.query.count()
    total_livros = models.Livro.query.filter_by(status=True).count()
    total_emprestimos = models.Emprestimo.query.filter_by(
        status=models.STATUS_ATIVO
    ).count()
    return render_template(
        "admin_painel.html",
        total_usuarios=total_usuarios,
        total_livros=total_livros,
        total_emprestimos=total_emprestimos,
    )

@app.route("/catalogo")
@login_required
def catalogo():
    return render_template("catalogo.html")

# Continuem com as outras funções abaixo

if __name__ == "__main__":
    app.run(debug=True)