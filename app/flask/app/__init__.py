from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from app.config import ProdConfig, DevConfig, TestConfig

import redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(ProdConfig)

    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'
    r = redis.Redis('localhost')

    return app, db, bcrypt, login_manager, r

app, db, bcrypt, login_manager, r = create_app()

from app.main.routes import main
from app.apis.data import data
from app.apis.auth import auth
app.register_blueprint(main)
app.register_blueprint(data)
app.register_blueprint(auth)



