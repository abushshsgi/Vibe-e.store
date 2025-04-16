import os
import logging
from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
babel = Babel()

def create_app():
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Set secret key
    app.secret_key = os.environ.get("SESSION_SECRET", "amazon-affiliate-secret-key")
    
    # Configure proxy fix for proper URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from routes.admin import admin_bp
    from routes.products import products_bp
    from routes.user import user_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(products_bp)
    app.register_blueprint(user_bp)
    
    # Set up Babel locale selector
    def get_locale():
        # Get language from URL parameter, user preference or request
        if request.args.get('lang'):
            lang = request.args.get('lang')
            session['lang'] = lang
            return lang
        elif session.get('lang'):
            return session.get('lang')
        return request.accept_languages.best_match(app.config['LANGUAGES_LIST'])
    
    babel.init_app(app, locale_selector=get_locale)
    
    # Set up theme preference
    @app.before_request
    def before_request():
        g.theme = session.get('theme', 'light')
        # Set current year for footer copyright
        g.current_year = datetime.datetime.now().year
        
    # Add context processor for global template variables
    @app.context_processor
    def inject_global_vars():
        from models import Category
        categories = Category.query.all()
        return dict(categories=categories)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
        
        # Initialize database with default category if empty
        from models import Category
        if not Category.query.first():
            from utils import initialize_database
            initialize_database()
    
    return app

# Import at the bottom to avoid circular imports
from flask import render_template
