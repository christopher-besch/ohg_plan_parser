import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config

# global app object
app = Flask(__name__)
# config
app.config.from_object(Config)
# database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# login
login = LoginManager(app)
login.login_view = 'auth.login'
# high level css
bootstrap = Bootstrap(app)
# time conversion
moment = Moment(app)

# activating logging when the application is not in debug mode
if not app.debug:
    # mail
    # only when a mail server is given
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Website Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # file
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/ohg_plan_parser.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('ohg_plan_parser startup')

# implementing blueprints
from app.main import bp as main_bp

app.register_blueprint(main_bp)

from app.auth import bp as auth_bp

app.register_blueprint(auth_bp)

from app.errors import bp as errors_bp

app.register_blueprint(errors_bp)

# implementing database models
from app import models
