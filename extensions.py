from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "entrar"
login_manager.login_message = "Faça login para continuar."
login_manager.login_message_category = "erro"