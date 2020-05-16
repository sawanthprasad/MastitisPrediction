from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextField, TextAreaField, SubmitField, FieldList, FormField, HiddenField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from wtforms_components import DateField, TimeField

#TODO: do some research on WTForms-Components: https://wtforms-components.readthedocs.io/en/latest/#


# forms are wrapped in classes. string, password, data, time, submit fields. Inherited from FlaskForm in flask_wtf

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)], render_kw = {"placeholder": "email"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=1, max=20)], render_kw = {"placeholder": "password"})
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])
    name = StringField('name')
    farm_address = StringField('current address')
    zip_code = StringField('zip code')
    city = StringField('city')
    state = StringField('state')
    country = StringField('country')
    phone = StringField('phone number')
    description = StringField('description')


class EditProfileForm(FlaskForm):
    name = StringField('Name')
    farm_address = StringField('Current address')
    zip_code = StringField('Zip Code')
    city = StringField('City')
    state = StringField('State')
    country = StringField('Country')
    phone = StringField('Phone number')
    description = StringField('description')
    

class NewProductForm(FlaskForm):
    product_name = StringField('product_name')
    price = StringField('price')
    category = SelectField('category', choices=[('Dairy', 'Dairy'), 
            ('Beverages','Beverages'), 
            ('Fruits','Fruits'), 
            ('Vegetables','Vegetables'),
            ('Meat', 'Meat'), 
            ('Fish','Fish'), 
            ('Eggs','Eggs'), 
            ('Snack','Snack'),
            ('Nuts', 'Nuts'), 
            ('Bread','Bread'), 
            ('Cereal','Cereal')])
    inventory = StringField('inventory')
    image = StringField('image')
    description = StringField('description')
    nutrition_facts = StringField('nutrition_facts')

class DonateNewProductForm(FlaskForm):
    product_name = StringField('product_name')
    category = SelectField('category', choices=[('Dairy', 'Dairy'), 
            ('Beverages','Beverages'), 
            ('Fruits','Fruits'), 
            ('Vegetables','Vegetables'),
            ('Meat', 'Meat'), 
            ('Fish','Fish'), 
            ('Eggs','Eggs'), 
            ('Snack','Snack'),
            ('Nuts', 'Nuts'), 
            ('Bread','Bread'), 
            ('Cereal','Cereal')])
    inventory = IntegerField('inventory')
    pickup_location = StringField('pickup_location')
    pickup_date= DateField('pickup_date')
    pickup_time = TimeField('pickup_time')
    image = StringField('image')

class PickupInfoForm(FlaskForm):
    pickup_location = StringField('pickup_location')
    pickup_date= DateField('pickup_date')
    pickup_time = TimeField('pickup_time')