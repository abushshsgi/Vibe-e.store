import os

class Config:
    # Application config
    DEBUG = True
    SECRET_KEY = os.environ.get("SESSION_SECRET", "amazon-affiliate-secret-key")
    
    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///amazon_affiliate.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # File uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Internationalization
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = [
        ('en', 'English'),
        ('ru', 'Russian')
    ]
    LANGUAGES_LIST = ['en', 'ru']
    
    # Amazon affiliate settings
    AMAZON_TRACKING_ID = os.environ.get("AMAZON_TRACKING_ID", "yourtag-20")
    
    # Application title
    SITE_NAME = "Amazon Affiliate Marketplace"
