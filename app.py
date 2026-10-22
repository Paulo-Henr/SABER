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

def validar_livro(form, livro_id=None)
    titulo = request.form.get("titulo", "").strip()
    autor = request.form.get("autor", "").strip()
    isbn = request.form.get("isbn", "").strip().replace("-", "").replace(" ", "")
    imagem = request.form.get("imagem", "").strip()
    
    generos_por_id = {str(g.id): g for g in models.listar_generos()}
    genero = generos_por_id.get(request.form.get("id_genero", ""))
    
    erros = []
    
    if not titulo:
        erros.append("Informe o título.")
    elif len(titulo) > 100:
        erros.append("O título deve ter no máximo 100 caracteres.")
    
    if not autor:
        erros.append("Informe o autor.")
    elif len(autor) > 100:
        erros.append("O autor deve ter no máximo 100 caracteres.")
    
    if not (isbn.isascii() and isbn.isdigit() and len(isbn) == 13):
        erros.append("O ISBN deve ter 13 números.")    
    if not imagem:
        erros.append("Informe a imagem.")
    if genero is None:
        erros.append("Selecione um gênero válido.")

    dados = {
        "titulo": titulo,
        "autor": autor,
        "isbn": isbn,
        "imagem": imagem,
        "genero": genero,
    }
    return erros, dados

@app.route("/admin/livros/novo", methods=["GET", "POST"])
@admin_required
def livro_novo():
    if request.method == "POST":
        erros, dados = validar_livro(request.form)

        if erros:
            return render_template(
                "admin_livro_novo.html",
                generos=models.listar_generos(),
                valores=request.form,
                erros=erros,
            )

        models.criar_livro(
            titulo=dados["titulo"],
            autor=dados["autor"],
            isbn=dados["isbn"],
            imagem=dados["imagem"],
            id_genero=dados["genero"].id,
            id_administrador=current_user.id,
        )
        flash("Livro cadastrado com sucesso.", "sucesso")
        return redirect(url_for("admin_painel"))

    return render_template(
        "admin_livro_novo.html",
        generos=models.listar_generos(),
        valores={},
        erros=[],
    )

@app.route("/admin/livros/<int:livro_id>/editar", methods=["GET", "POST"])
@admin_required

def admin_livro_editar(livro_id):
    livro = models.buscar_livro(livro_id)
    if livro is None:
        abort(404)

    if request.method == "POST":
        erros, dados = validar_livro(request.form, livro_id)

        if erros:
            return render_template(
                "admin_editar.html",
                livro=livro,
                generos=models.listar_generos(),
                valores=request.form,
                erros=erros,
            )

        models.atualizar_livro(
            livro_id,
            titulo=dados["titulo"],
            autor=dados["autor"],
            isbn=dados["isbn"],
            imagem=dados["imagem"],
            id_genero=dados["genero"].id,
        )
        flash("Livro atualizado com sucesso.", "sucesso") 
        return redirect(url_for("admin_painel"))

    return render_template(
        "admin_livro_editar.html",
        livro=livro,
        generos=models.listar_generos(),
        valores={},
        erros=[],
    )

# Continuem com as outras funções abaixo

if __name__ == "__main__":
    app.run(debug=True)