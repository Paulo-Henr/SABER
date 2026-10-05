from datetime import datetime

import psycopg2
from psycopg2 import sql
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from extensions import db

STATUS_ATIVO = "ativo"
STATUS_DEVOLVIDO = "devolvido"

TIPO_ADMIN = "admin"
TIPO_USUARIO = "usuario"

def criar_banco_se_nao_existir():
    conexao = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        dbname="postgres",
    )
    conexao.autocommit = True
    cursor = conexao.cursor()
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (Config.DB_NOME,))
    if cursor.fetchone() is None:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(Config.DB_NOME))
        )
    cursor.close()
    conexao.close()

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(25), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(15))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def get_id(self):
        return f"{TIPO_USUARIO}:{self.id}"
 
    @property
    def is_admin(self):
        return False
 
    def __repr__(self):
        return f"<Usuario {self.id} - {self.email}>"

class Administrador(db.Model, UserMixin):
    __tablename__ = "administrador"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
 
    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
 
    def get_id(self):
        return f"{TIPO_ADMIN}:{self.id}"
 
    @property
    def is_admin(self):
        return True
 
    def __repr__(self):
        return f"<Administrador {self.id} - {self.email}>"

class Genero(db.Model):
    __tablename__ = "genero"
 
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
 
    def __repr__(self):
        return f"<Genero {self.nome}>"

class Livro(db.Model):
    __tablename__ = "livro"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    imagem = db.Column(db.String(254), nullable=False)

    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id"), nullable=False)
    genero = db.relationship("Genero", backref=db.backref("livros", lazy=True))

    id_administrador_cadastro = db.Column(db.Integer, db.ForeignKey("administrador.id", ondelete="SET NULL"))
    administrador = db.relationship("Administrador")

    # Nota: True = está no acervo | False = removido
    status = db.Column(db.Boolean, default=True, nullable=False)
    # Nota: True = livre | False = emprestado
    disponibilidade = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Livro {self.id} - {self.titulo}>"

class Emprestimo(db.Model):
    __tablename__ = "emprestimo"

    id = db.Column(db.Integer, primary_key=True)

    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", backref=db.backref("emprestimos", lazy=True))

    id_livro = db.Column(db.Integer, db.ForeignKey("livro.id"), nullable=False)
    livro = db.relationship("Livro", backref=db.backref("emprestimos", lazy=True))

    data_retirada = db.Column(db.DateTime, nullable=False)
    data_devolucao_prevista = db.Column(db.DateTime, nullable=False)
    data_devolucao_real = db.Column(db.DateTime)

    status = db.Column(db.String(20), default=STATUS_ATIVO, nullable=False)
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Emprestimo {self.id} - livro {self.id_livro} / usuário {self.id_usuario}>"

def carregar_conta(identificador):
    try:
        tipo, id_texto = identificador.split(":")
        id_conta = int(id_texto)
    except (ValueError, AttributeError):
        return None

    if tipo == TIPO_ADMIN:
        return db.session.get(Administrador, id_conta)
    if tipo == TIPO_USUARIO:
        return db.session.get(Usuario, id_conta)
    return None

def buscar_conta_por_email(email):
    conta = Administrador.query.filter_by(email=email).first()
    if conta is None:
        conta = Usuario.query.filter_by(email=email).first()
    return conta

# O mesmo e-mail não pode estar nas duas tabelas diferentes, pois isso, essa função garante isso no cadastro
def email_em_uso(email):
    return buscar_conta_por_email(email) is not None

def listar_generos():
    return Genero.query.order_by(Genero.nome).all()

def buscar_livro(livro_id):
    return db.session.get(Livro, livro_id)

# Continuem com as outras funções abaixo