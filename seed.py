from datetime import datetime

from extensions import db
from models import Administrador, Emprestimo, Genero, Livro, Usuario, STATUS_ATIVO, STATUS_DEVOLVIDO

# Nota: as contas abaixo são de TESTE para o desenvolvimento
ADMINISTRADORES = [
    {"nome": "Admin123", "email": "teste.admin@gmail.com", "senha": "admin123"},
]

USUARIOS = [
    {"nome": "Diego_Samuel", "senha": "diego1234", "telefone": "11987654321", "cpf": "12345678901", "email": "diego@gmail.com"},
    {"nome": "Thalys_Rafael", "senha": "thalys1234", "telefone": "21976543210", "cpf": "98765432100", "email": "thalys@gmail.com"},
    {"nome": "Paulo_Henrique", "senha": "paulo1234", "telefone": "21987654321", "cpf": "98765432101", "email": "paulo@gmail.com"},
    {"nome": "Victor_Manoel", "senha": "victor1234", "telefone": "31965432109", "cpf": "45678912300", "email": "victor@gmail.com"},
]

GENEROS = [
    "Ação", "Aventura", "Biografia", "Clássico", "Comédia", "Drama", "Fantasia", "Ficção Científica", "História", "Horror", "Infantil",
    "Juvenil", "Mistério", "Poesia", "Romance", "Suspense", "Terror", "Thriller", "Novela", "Autobiografia",
]

LIVROS = [
    {"titulo": "O Alquimista", "autor": "Paulo Coelho", "isbn": "9788576653929", "imagem": "https://placehold.co/200x300?text=O+Alquimista", "genero": "Romance", "disponibilidade": True},
    {"titulo": "Dom Casmurro", "autor": "Machado de Assis", "isbn": "9788535902778", "imagem": "https://placehold.co/200x300?text=Dom+Casmurro", "genero": "Clássico", "disponibilidade": False},  # está emprestado
    {"titulo": "1984", "autor": "George Orwell", "isbn": "9788535914849", "imagem": "https://placehold.co/200x300?text=1984", "genero": "Ficção Científica", "disponibilidade": True},
]

EMPRESTIMOS = [
    {"usuario": "diego@gmail.com", "isbn": "9788535902778", "retirada": datetime(2026, 3, 1, 10, 0), "prevista": datetime(2026, 3, 15, 10, 0), "real": None, "status": STATUS_ATIVO},
    {"usuario": "thalys@gmail.com", "isbn": "9788576653929", "retirada": datetime(2026, 2, 10, 14, 30), "prevista": datetime(2026, 2, 24, 14, 30), "real": datetime(2026, 2, 22, 11, 15), "status": STATUS_DEVOLVIDO},
]

def popular_dados_exemplo():
    if Administrador.query.count() == 0:
        for a in ADMINISTRADORES:
            admin = Administrador(nome=a["nome"], email=a["email"])
            admin.definir_senha(a["senha"])
            db.session.add(admin)
        db.session.commit()

    if Genero.query.count() == 0:
        for nome in GENEROS:
            db.session.add(Genero(nome=nome))
        db.session.commit()

    if Usuario.query.count() == 0:
        for u in USUARIOS:
            usuario = Usuario(nome=u["nome"], telefone=u["telefone"], cpf=u["cpf"], email=u["email"])
            usuario.definir_senha(u["senha"])
            db.session.add(usuario)
        db.session.commit()

    if Livro.query.count() == 0:
        generos_por_nome = {g.nome: g for g in Genero.query.all()}
        admin = Administrador.query.first()
        for l in LIVROS:
            db.session.add(Livro(
                titulo=l["titulo"],
                autor=l["autor"],
                isbn=l["isbn"],
                imagem=l["imagem"],
                id_genero=generos_por_nome[l["genero"]].id,
                id_administrador_cadastro=admin.id if admin else None,
                disponibilidade=l["disponibilidade"],
            ))
        db.session.commit()

    if Emprestimo.query.count() == 0:
        usuarios_por_email = {u.email: u for u in Usuario.query.all()}
        livros_por_isbn = {l.isbn: l for l in Livro.query.all()}
        for e in EMPRESTIMOS:
            db.session.add(Emprestimo(
                id_usuario=usuarios_por_email[e["usuario"]].id,
                id_livro=livros_por_isbn[e["isbn"]].id,
                data_retirada=e["retirada"],
                data_devolucao_prevista=e["prevista"],
                data_devolucao_real=e["real"],
                status=e["status"],
            ))
        db.session.commit()

if __name__ == "__main__":
    from app import app

    with app.app_context():
        popular_dados_exemplo()
        print("Banco populado com administrador, usuários, gêneros, livros e empréstimos de TESTE.")