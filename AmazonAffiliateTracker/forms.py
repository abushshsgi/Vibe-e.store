from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, FloatField, BooleanField, SelectField, MultipleFileField, IntegerField
from wtforms.validators import DataRequired, URL, Optional, NumberRange
from flask_babel import lazy_gettext as _l
from app import db
from models import Category

class CategoryForm(FlaskForm):
    name = StringField(_l('Category Name'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    
    # Translations
    name_ru = StringField(_l('Name (Russian)'), validators=[Optional()])
    description_ru = TextAreaField(_l('Description (Russian)'), validators=[Optional()])

class ProductForm(FlaskForm):
    title = StringField(_l('Product Title'), validators=[DataRequired()])
    description = TextAreaField(_l('Description'), validators=[Optional()])
    price = FloatField(_l('Price'), validators=[DataRequired(), NumberRange(min=0.01)])
    amazon_link = StringField(_l('Amazon Link'), validators=[DataRequired(), URL()])
    category_id = SelectField(_l('Category'), coerce=int, validators=[DataRequired()])
    is_new = BooleanField(_l('New Product'))
    is_hot = BooleanField(_l('Hot Product'))
    is_trending = BooleanField(_l('Trending Product'))
    featured = BooleanField(_l('Featured Product'))
    rating = SelectField(_l('Rating (0-5 stars)'), choices=[(0, '0 - No rating'), (1, '1 star'), (2, '2 stars'), 
                                                       (3, '3 stars'), (4, '4 stars'), (5, '5 stars')], 
                        coerce=int, default=0)
    images = MultipleFileField(_l('Product Images'), validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], _l('Images only'))])
    
    # Translations
    title_ru = StringField(_l('Title (Russian)'), validators=[Optional()])
    description_ru = TextAreaField(_l('Description (Russian)'), validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

class BannerForm(FlaskForm):
    title = StringField(_l('Banner Title'), validators=[DataRequired()])
    link = StringField(_l('Banner Link'), validators=[Optional(), URL()])
    image = FileField(_l('Banner Image'), validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], _l('Images only'))
    ])
    is_active = BooleanField(_l('Active'), default=True)
    
    # Translations
    title_ru = StringField(_l('Title (Russian)'), validators=[Optional()])

class SearchForm(FlaskForm):
    query = StringField(_l('Search'), validators=[DataRequired()])
