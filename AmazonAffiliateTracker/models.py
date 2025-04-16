from app import db
import datetime
from sqlalchemy import func
from slugify import slugify
import uuid
import json

# Product-related models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)
    
    # Translations
    name_ru = db.Column(db.String(100), nullable=True)
    description_ru = db.Column(db.Text, nullable=True)
    
    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('name', ''))
        super(Category, self).__init__(*args, **kwargs)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    amazon_link = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    is_new = db.Column(db.Boolean, default=True)
    is_hot = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer, default=0)  # Rating 0-5 (0 = no rating)
    featured = db.Column(db.Boolean, default=False)  # Featured product for homepage
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)
    
    # Translations
    title_ru = db.Column(db.String(200), nullable=True)
    description_ru = db.Column(db.Text, nullable=True)
    
    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', '')) + '-' + str(uuid.uuid4())[:8]
        super(Product, self).__init__(*args, **kwargs)
    
    def get_primary_image(self):
        primary = next((img for img in self.images if img.is_primary), None)
        return primary or (self.images[0] if self.images else None)
    
    def get_view_count(self):
        return db.session.query(func.count(ProductView.id)).filter(ProductView.product_id == self.id).scalar()
    
    def get_click_count(self):
        return db.session.query(func.count(ProductClick.id)).filter(ProductClick.product_id == self.id).scalar()
    
    def __repr__(self):
        return f'<Product {self.title}>'

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductImage {self.filename}>'

# Banner model
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(500), nullable=True)
    filename = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Translations
    title_ru = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Banner {self.title}>'

# Analytics models
class ProductView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('views', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<ProductView {self.product_id} at {self.timestamp}>'

class ProductClick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('clicks', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<ProductClick {self.product_id} at {self.timestamp}>'

# User wishlist
class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('wishlist_items', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<WishlistItem {self.product_id}>'
