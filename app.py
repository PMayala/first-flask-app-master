import os

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
import models

from resources.household import household_blp
from resources.request import request_blp
from resources.user import user_blp
from resources.admin import admin_blp

def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "EchoTrack API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui/api/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///db.sqlite")
    db.init_app(app)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "suprise-suprise-mf"
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

    api.register_blueprint(admin_blp)
    api.register_blueprint(household_blp)
    api.register_blueprint(request_blp)
    api.register_blueprint(user_blp)
    
    return app