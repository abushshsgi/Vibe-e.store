from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import os
import uuid

from app import db
from models import Product, Category, Banner, ProductImage, ProductView, ProductClick
from forms import ProductForm, CategoryForm, BannerForm
from utils import save_uploaded_file, get_date_range

admin_bp = Blueprint('admin', __name__)

# Dashboard
@admin_bp.route('/')
def dashboard():
    # Get statistics
    total_products = Product.query.count()
    total_categories = Category.query.count()
    total_banners = Banner.query.filter_by(is_active=True).count()
    
    # Get view/click data for charts
    start_date, end_date, date_list = get_date_range(days=7)
    
    # Get most viewed products
    most_viewed = db.session.query(
        Product, func.count(ProductView.id).label('view_count')
    ).join(ProductView).group_by(Product.id).order_by(desc('view_count')).limit(5).all()
    
    # Get recent views
    recent_views = db.session.query(ProductView).join(Product).order_by(
        ProductView.timestamp.desc()
    ).limit(10).all()
    
    # Get view count per day for chart
    view_counts = []
    for i in range(7):
        day = end_date - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        count = db.session.query(func.count(ProductView.id)).filter(
            ProductView.timestamp.between(day_start, day_end)
        ).scalar()
        
        view_counts.append(count or 0)
    
    view_counts.reverse()  # Reverse to show in chronological order
    
    return render_template(
        'admin/dashboard.html',
        total_products=total_products,
        total_categories=total_categories,
        total_banners=total_banners,
        most_viewed=most_viewed,
        recent_views=recent_views,
        view_counts=view_counts,
        date_list=date_list
    )

# API endpoints for dashboard charts
@admin_bp.route('/api/stats/daily_views')
def api_daily_views():
    days = int(request.args.get('days', 7))
    start_date, end_date, date_list = get_date_range(days=days)
    
    # Query daily views
    daily_views = []
    for i in range(days):
        day = end_date - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        count = db.session.query(func.count(ProductView.id)).filter(
            ProductView.timestamp.between(day_start, day_end)
        ).scalar()
        
        daily_views.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count or 0
        })
    
    daily_views.reverse()  # Chronological order
    
    return jsonify({
        'labels': [item['date'] for item in daily_views],
        'data': [item['count'] for item in daily_views]
    })

@admin_bp.route('/api/stats/product_views')
def api_product_views():
    # Get top products by view count
    top_products = db.session.query(
        Product, func.count(ProductView.id).label('view_count')
    ).join(ProductView).group_by(Product.id).order_by(desc('view_count')).limit(5).all()
    
    return jsonify({
        'labels': [product.title for product, _ in top_products],
        'data': [count for _, count in top_products]
    })

@admin_bp.route('/api/stats/product_clicks')
def api_product_clicks():
    # Get top products by click count
    top_products = db.session.query(
        Product, func.count(ProductClick.id).label('click_count')
    ).join(ProductClick).group_by(Product.id).order_by(desc('click_count')).limit(5).all()
    
    return jsonify({
        'labels': [product.title for product, _ in top_products],
        'data': [count for _, count in top_products]
    })

@admin_bp.route('/api/stats/conversion_rate')
def api_conversion_rate():
    # Get product conversion rates (clicks / views)
    products_with_stats = db.session.query(
        Product,
        func.count(ProductView.id).label('view_count'),
        func.count(ProductClick.id).label('click_count')
    ).outerjoin(ProductView).outerjoin(ProductClick).group_by(Product.id).all()
    
    result = []
    total_views = 0
    total_clicks = 0
    
    for product, view_count, click_count in products_with_stats:
        if view_count > 0:
            rate = (click_count / view_count) * 100
            total_views += view_count
            total_clicks += click_count
            
            result.append({
                'product': product.title,
                'views': view_count,
                'clicks': click_count,
                'rate': round(rate, 2)
            })
    
    # Sort by conversion rate
    result.sort(key=lambda x: x['rate'], reverse=True)
    
    # Calculate overall conversion rate
    overall_rate = 0
    if total_views > 0:
        overall_rate = (total_clicks / total_views) * 100
    
    return jsonify({
        'overall_rate': round(overall_rate, 2),
        'products': result[:10]  # Top 10 products
    })

# Category routes
@admin_bp.route('/categories')
def categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            name_ru=form.name_ru.data,
            description_ru=form.description_ru.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(_('Category added successfully'), 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form)

@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.name_ru = form.name_ru.data
        category.description_ru = form.description_ru.data
        category.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(_('Category updated successfully'), 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/category_form.html', form=form, category=category)

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has products
    if category.products:
        flash(_('Cannot delete category that has products'), 'danger')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash(_('Category deleted successfully'), 'success')
    return redirect(url_for('admin.categories'))

# Product routes
@admin_bp.route('/products')
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            amazon_link=form.amazon_link.data,
            category_id=form.category_id.data,
            is_new=form.is_new.data,
            is_hot=form.is_hot.data,
            is_trending=form.is_trending.data,
            featured=form.featured.data,
            rating=form.rating.data,
            title_ru=form.title_ru.data,
            description_ru=form.description_ru.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Handle image uploads
        new_images = request.files.getlist('images')
        if new_images:
            for i, image_data in enumerate(new_images):
                if image_data and image_data.filename:
                    filename = save_uploaded_file(image_data, 'products')
                    if filename:
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=(i == 0)  # First image is primary
                        )
                        db.session.add(image)
            
            db.session.commit()
        
        flash(_('Product added successfully'), 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', form=form)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.amazon_link = form.amazon_link.data
        product.category_id = form.category_id.data
        product.is_new = form.is_new.data
        product.is_hot = form.is_hot.data
        product.is_trending = form.is_trending.data
        product.featured = form.featured.data
        product.rating = form.rating.data
        product.title_ru = form.title_ru.data
        product.description_ru = form.description_ru.data
        product.updated_at = datetime.utcnow()
        
        # Handle primary image
        primary_image_id = request.form.get('primary_image')
        if primary_image_id:
            for image in product.images:
                image.is_primary = (str(image.id) == primary_image_id)
        
        # Handle image deletions
        delete_images = request.form.getlist('delete_image')
        if delete_images:
            for image_id in delete_images:
                image = ProductImage.query.get(image_id)
                if image and image.product_id == product.id:
                    # Delete file if exists
                    file_path = os.path.join('static/uploads', image.filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    db.session.delete(image)
        
        # Handle new image uploads
        new_images = request.files.getlist('new_images') if 'new_images' in request.files else None
        if new_images:
            for i, image_data in enumerate(new_images):
                if image_data and image_data.filename:
                    filename = save_uploaded_file(image_data, 'products')
                    if filename:
                        # If no existing images and this is the first upload, make it primary
                        is_primary = not product.images and i == 0
                        
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=is_primary
                        )
                        db.session.add(image)
        elif form.images.data:
            # Check standard form field if no new_images (for new products)
            for i, image_data in enumerate(form.images.data):
                if image_data:
                    filename = save_uploaded_file(image_data, 'products')
                    if filename:
                        # If no existing images and this is the first upload, make it primary
                        is_primary = not product.images and i == 0
                        
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=is_primary
                        )
                        db.session.add(image)
        
        db.session.commit()
        
        flash(_('Product updated successfully'), 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/product_form.html', form=form, product=product)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Delete associated images
    for image in product.images:
        file_path = os.path.join('static/uploads', image.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash(_('Product deleted successfully'), 'success')
    return redirect(url_for('admin.products'))

# Banner routes
@admin_bp.route('/banners')
def banners():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('admin/banners.html', banners=banners)

@admin_bp.route('/banners/add', methods=['GET', 'POST'])
def add_banner():
    form = BannerForm()
    
    if form.validate_on_submit():
        # Save banner image
        filename = save_uploaded_file(form.image.data, 'banners')
        
        if filename:
            banner = Banner(
                title=form.title.data,
                link=form.link.data,
                filename=filename,
                is_active=form.is_active.data,
                title_ru=form.title_ru.data
            )
            
            db.session.add(banner)
            db.session.commit()
            
            flash(_('Banner added successfully'), 'success')
            return redirect(url_for('admin.banners'))
        else:
            flash(_('Error uploading image'), 'danger')
    
    return render_template('admin/banner_form.html', form=form)

@admin_bp.route('/banners/edit/<int:id>', methods=['GET', 'POST'])
def edit_banner(id):
    banner = Banner.query.get_or_404(id)
    form = BannerForm(obj=banner)
    
    # Don't require image upload on edit
    form.image.validators = [FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], _('Images only'))]
    
    if form.validate_on_submit():
        banner.title = form.title.data
        banner.link = form.link.data
        banner.is_active = form.is_active.data
        banner.title_ru = form.title_ru.data
        banner.updated_at = datetime.utcnow()
        
        # Handle image update if provided
        if form.image.data:
            # Delete old image
            old_file_path = os.path.join('static/uploads', banner.filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            
            # Save new image
            filename = save_uploaded_file(form.image.data, 'banners')
            if filename:
                banner.filename = filename
        
        db.session.commit()
        
        flash(_('Banner updated successfully'), 'success')
        return redirect(url_for('admin.banners'))
    
    return render_template('admin/banner_form.html', form=form, banner=banner)

@admin_bp.route('/banners/delete/<int:id>', methods=['POST'])
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    
    # Delete banner image
    file_path = os.path.join('static/uploads', banner.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(banner)
    db.session.commit()
    
    flash(_('Banner deleted successfully'), 'success')
    return redirect(url_for('admin.banners'))
