from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
import json  # Importa el módulo json de Flask


db = SQLAlchemy()
jwt = JWTManager()

# Definir el filtro primero
def replace_keywords(text, keywords):
    for keyword, replacement in keywords.items():
        text = text.replace(f'{{{{{keyword}}}}}', replacement)  # Corregido formato de llaves
    return text

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.json_encoder = json.JSONEncoder  # Usa el JSONEncoder de Flask

    
    
    # Registrar el filtro personalizado
    app.jinja_env.filters['replace_keywords'] = replace_keywords
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    from app.routes import routes, main_bp
    app.register_blueprint(routes)
    app.register_blueprint(main_bp)

    return app  # Corregida indentación


    
    

