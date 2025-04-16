from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, g, abort
from flask_babel import gettext as _
from sqlalchemy import func, desc
import uuid
from datetime import datetime

from app import db
from models import Product, Category, Banner, ProductView, ProductClick
from forms import SearchForm
from utils import format_amazon_link

products_bp = Blueprint('products', __name__)

# Home page
@products_bp.route('/')
def index():
    # Get active banners
    banners = Banner.query.filter_by(is_active=True).all()
    
    # Get featured products
    new_products = Product.query.filter_by(is_new=True).order_by(Product.created_at.desc()).limit(8).all()
    trending_products = Product.query.filter_by(is_trending=True).order_by(Product.created_at.desc()).limit(8).all()
    hot_products = Product.query.filter_by(is_hot=True).order_by(Product.created_at.desc()).limit(8).all()
    
    # Get popular categories
    popular_categories = Category.query.join(Category.products).group_by(Category.id).order_by(
        func.count(Product.id).desc()
    ).limit(6).all()
    
    return render_template(
        'index.html',
        banners=banners,
        new_products=new_products,
        trending_products=trending_products,
        hot_products=hot_products,
        popular_categories=popular_categories,
        search_form=SearchForm()
    )

# Product detail page
@products_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    
    # Record product view
    record_product_view(product)
    
    # Get related products from same category
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).order_by(func.random()).limit(4).all()
    
    # Format Amazon link with tracking ID
    amazon_link = format_amazon_link(product.amazon_link)
    
    return render_template(
        'product_detail.html',
        product=product,
        related_products=related_products,
        amazon_link=amazon_link,
        search_form=SearchForm()
    )

# Category products page
@products_bp.route('/category/<slug>')
def category_products(slug):
    category = Category.query.filter_by(slug=slug).first_or_404()
    
    # Get sorting parameter
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = Product.query.filter_by(category_id=category.id)
    
    if sort == 'price_low':
        query = query.order_by(Product.price)
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        # Order by view count (subquery for performance)
        view_counts = db.session.query(
            ProductView.product_id,
            func.count(ProductView.id).label('view_count')
        ).group_by(ProductView.product_id).subquery()
        
        query = query.outerjoin(
            view_counts, Product.id == view_counts.c.product_id
        ).order_by(desc(view_counts.c.view_count), Product.created_at.desc())
    else:  # Default: newest
        query = query.order_by(Product.created_at.desc())
    
    # Paginate results
    products = query.paginate(page=page, per_page=12)
    
    return render_template(
        'category_products.html',
        category=category,
        products=products,
        current_sort=sort,
        search_form=SearchForm()
    )

# Search results
@products_bp.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    if form.validate_on_submit():
        return redirect(url_for('products.search', q=form.query.data))
    
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('products.index'))
    
    page = request.args.get('page', 1, type=int)
    
    # Search in product title and description
    search_results = Product.query.filter(
        (Product.title.ilike(f'%{query}%')) | 
        (Product.description.ilike(f'%{query}%'))
    ).order_by(Product.created_at.desc()).paginate(page=page, per_page=12)
    
    return render_template(
        'search_results.html',
        search_query=query,
        products=search_results,
        search_form=form
    )

# Product click tracker
@products_bp.route('/track/click/<int:product_id>')
def track_click(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Record product click
    click = ProductClick(
        product_id=product.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(click)
    db.session.commit()
    
    # Format Amazon link with tracking ID
    amazon_link = format_amazon_link(product.amazon_link)
    
    return jsonify({'success': True, 'redirect': amazon_link})

# Helper function for recording product views
def record_product_view(product):
    # Check if user has already viewed this product in this session
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    
    # Record view only once per session
    existing_view = ProductView.query.filter_by(
        product_id=product.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    ).order_by(ProductView.timestamp.desc()).first()
    
    # If no view exists or last view was more than a day ago
    if not existing_view or (datetime.utcnow() - existing_view.timestamp).days >= 1:
        view = ProductView(
            product_id=product.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(view)
        db.session.commit()

# Error handlers
@products_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', search_form=SearchForm()), 404

@products_bp.app_errorhandler(500)
def server_error(e):
    return render_template('500.html', search_form=SearchForm()), 500
