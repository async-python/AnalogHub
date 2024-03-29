import flask_login
from auth.users import handle_needs_login, load_user
from auth.views import user_auth
from core.conf import FlaskConfig
from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate
from src.ctx_processor import year_processor
from src.database import db
from src.views import analog


def create_app():
    analog_app = Flask(__name__)
    analog_app.config.from_object(FlaskConfig)
    login_manager = flask_login.LoginManager()
    login_manager.init_app(analog_app)
    login_manager.user_loader(load_user)
    login_manager.unauthorized_handler(handle_needs_login)
    Bootstrap4(analog_app)
    with analog_app.app_context():
        db.init_app(analog_app)
    Migrate(analog_app, db)
    analog_app.context_processor(year_processor)
    analog_app.register_blueprint(analog, url_prefix='')
    analog_app.register_blueprint(user_auth, url_prefix='/auth')
    return analog_app


if __name__ == '__main__':
    create_app().run(host='0.0.0.0')
