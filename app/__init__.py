#app/__init__.py
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from flask_wtf.csrf import CSRFProtect
from config import config
from sqlalchemy import inspect
from flask_jwt_extended.exceptions import JWTExtendedException

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
csrf = CSRFProtect()

def create_app(config_name='development'):
    app = Flask(__name__)
    logger = logging.getLogger(__name__)
    logger.debug("Creating app CUI Linkedin...")

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection

    # Context processor to inject app config into templates
    @app.context_processor
    def inject_app_config():
        return dict(app_config=app.config)

    # import revoked from model 
    from .models import is_token_revoked

    # Add the token blocklist loader
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload)

    # Print the database URI for debugging
    logger.debug(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Check if the database is initialized
    with app.app_context():
        if not database_exists(db.engine):
            app.logger.warning("Database does not exist. Please run create_tables.py to initialize it.")
        elif not tables_exist(db.engine):
            app.logger.warning("Tables do not exist. Please run create_tables.py to create them.")
        else:
            app.logger.debug("Database and tables exist.")

    # Register error handlers
    register_error_handlers(app)

    # Register JWT error handlers
    register_jwt_error_handlers(app)

    logger.debug("App CUI created successfully")
    return app

def database_exists(engine):
    try:
        with engine.connect() as conn:
            return True
    except Exception as e:
        logging.error(f"Error checking if database exists: {str(e)}")
        return False

def tables_exist(engine):
    try:
        inspector = inspect(engine)
        return len(inspector.get_table_names()) > 0
    except Exception as e:
        logging.error(f"Error checking if tables exist: {str(e)}")
        return False

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(error):
        app.logger.error(f"JWT Exception: {str(error)}")
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("An error occurred with your session. Please log in again.", "warning")
        return resp

def register_jwt_error_handlers(app):
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("You must be logged in to access this page.", "warning")
        return resp

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        app.logger.debug(f"Invalid token: {error_string}")
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("Invalid token. Please log in again.", "warning")
        return resp

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("You need to login again to access this page.", "warning")
        return resp

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("Your session has expired. Please log in again.", "warning")
        return resp

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        resp = make_response(redirect(url_for('main.login')))
        unset_jwt_cookies(resp)
        flash("Your session has been revoked. Please log in again.", "warning")
        return resp