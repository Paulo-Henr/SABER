from flask import Flask, abort, redirect, render_template, request, url_for
import models
import seed
from extensions import db, login_manager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

models.criar_banco_se_nao_existir()

db.init_app(app)

with app.app_context():
    db.create_all()

    seed.popular_dados_exemplo()

@login_manager.user_loader
def carregar_usuario(identificador):
    return models.carregar_conta(identificador)


@app.route("/")
def index():
    return f"SABER no a. Livros cadastrados no banco: {models.Livro.query.count()}" 

# Continuem com as outras funções abaixo

if __name__ == "__main__":
    app.run(debug=True)