from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_babel import gettext as _
import uuid

from app import db
from models import Product, WishlistItem
from forms import SearchForm

user_bp = Blueprint('user', __name__)

# Wishlist page
@user_bp.route('/wishlist')
def wishlist():
    # Get session ID
    session_id = get_or_create_session_id()
    
    # Get wishlist items
    wishlist_items = WishlistItem.query.filter_by(session_id=session_id).join(
        Product
    ).with_entities(
        WishlistItem, Product
    ).order_by(WishlistItem.created_at.desc()).all()
    
    return render_template(
        'wishlist.html',
        wishlist_items=wishlist_items,
        search_form=SearchForm()
    )

# Add product to wishlist
@user_bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    # Get session ID
    session_id = get_or_create_session_id()
    
    # Check if product exists
    product = Product.query.get_or_404(product_id)
    
    # Check if product already in wishlist
    existing_item = WishlistItem.query.filter_by(
        session_id=session_id,
        product_id=product_id
    ).first()
    
    if existing_item:
        return jsonify({
            'success': False,
            'message': _('Product already in wishlist')
        })
    
    # Add product to wishlist
    wishlist_item = WishlistItem(
        session_id=session_id,
        product_id=product_id
    )
    
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': _('Product added to wishlist')
    })

# Remove product from wishlist
@user_bp.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    # Get session ID
    session_id = get_or_create_session_id()
    
    # Find and delete wishlist item
    wishlist_item = WishlistItem.query.filter_by(
        session_id=session_id,
        product_id=product_id
    ).first_or_404()
    
    db.session.delete(wishlist_item)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': _('Product removed from wishlist')
        })
    
    return redirect(url_for('user.wishlist'))

# Theme switcher
@user_bp.route('/theme/<theme>')
def set_theme(theme):
    if theme not in ['light', 'dark']:
        theme = 'light'
    
    session['theme'] = theme
    
    # Get the previous URL or default to home
    next_url = request.args.get('next') or request.referrer or url_for('products.index')
    
    return redirect(next_url)

# Language switcher
@user_bp.route('/language/<lang>')
def set_language(lang):
    # Validate language code
    from app import create_app
    allowed_langs = create_app().config['LANGUAGES_LIST']
    
    if lang not in allowed_langs:
        lang = 'en'
    
    session['lang'] = lang
    
    # Get the previous URL or default to home
    next_url = request.args.get('next') or request.referrer or url_for('products.index')
    
    return redirect(next_url)

# Helper function to get or create session ID
def get_or_create_session_id():
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
    return session_id
