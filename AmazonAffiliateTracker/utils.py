import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from models import Category, db

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, folder=''):
    """Save an uploaded file and return the filename"""
    if file and allowed_file(file.filename):
        # Generate a unique filename to prevent overwrites
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Return path relative to UPLOAD_FOLDER
        return os.path.join(folder, unique_filename) if folder else unique_filename
    
    return None

def get_date_range(days=7):
    """Get date range for statistics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Create list of dates
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return start_date, end_date, date_list

def format_amazon_link(link, tracking_id=None):
    """Format Amazon link with tracking ID if not already present"""
    if not tracking_id:
        tracking_id = current_app.config.get('AMAZON_TRACKING_ID', 'yourtag-20')
    
    # If link already has a tag parameter, return as is
    if 'tag=' in link:
        return link
    
    # Check if link has query parameters
    if '?' in link:
        return f"{link}&tag={tracking_id}"
    else:
        return f"{link}?tag={tracking_id}"

def initialize_database():
    """Initialize database with default categories if empty"""
    try:
        # Add default categories
        default_categories = [
            {
                'name': 'Electronics',
                'description': 'Electronic gadgets and devices',
                'name_ru': 'Электроника',
                'description_ru': 'Электронные гаджеты и устройства'
            },
            {
                'name': 'Books',
                'description': 'Books of all genres',
                'name_ru': 'Книги',
                'description_ru': 'Книги всех жанров'
            },
            {
                'name': 'Home & Kitchen',
                'description': 'Products for your home and kitchen',
                'name_ru': 'Дом и Кухня',
                'description_ru': 'Товары для дома и кухни'
            },
            {
                'name': 'Fashion',
                'description': 'Clothing, shoes, and accessories',
                'name_ru': 'Мода',
                'description_ru': 'Одежда, обувь и аксессуары'
            }
        ]
        
        for category_data in default_categories:
            category = Category(**category_data)
            db.session.add(category)
        
        db.session.commit()
        print("Default categories created successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing database: {str(e)}")
