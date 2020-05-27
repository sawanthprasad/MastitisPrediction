from flask import Flask, render_template, redirect, url_for, flash
from flask import request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm, EditProfileForm
from datetime import datetime
import json
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.documents as documents
import azure.cosmos.http_constants as http_constants

# App instance
app = Flask(__name__) # __name__ == "__main__" when executing the script
app.config.from_object('config.Config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app) # orm relation added
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------- Models -----------------------
class User(UserMixin, db.Model): #multiple inheritance
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    name = db.Column(db.String(50))
    farm_address = db.Column(db.String(50))
    zip_code = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    description = db.Column(db.String(50))

# @app.errorhandler(404)
# def page_not_found(e):
    # app.logger.error('Page not found: %s', (request.path))
    # return render_template('404.html'), 404

@app.errorhandler(404)
def not_found(error):
    return render_template('404_backup.html'), 404

# Set up user_loader 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# client = MongoClient("cattlecare-db.mongo.cosmos.azure.com:10255") #host uri
# db = client.test
# db.authenticate(name="cattlecare-db", password='UP62PDTb78l7nNgfEOHqAwEvCOLff3lTrkmUJWQIoLyJjan2IprAY0kos4yZCriJGzFV5a6IWtIkfoauW35Idw==')
# collection = db.test_collection

endpoint = 'https://cattlecare-database.documents.azure.com:443/'
key = 'KRLlbNOhbBZgKvonG3wzBvjDsWEOBgZ1rwK1hE655v0ihue0fRo3ZLXR9hCy2jSAykZPRfgWB9vR7D3AcmU0ew=='
client = cosmos_client.CosmosClient(endpoint, key)

database_name = 'db_predictions'
container_name = 'con_predictions'

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)
aid = "'102'"
# query = "SELECT c.Prediction FROM con_predictions c where c.AnimalID = " + aid
query = "SELECT * from c"
print(query)
database_link = 'dbs/' + database_name
collection_link = database_link + '/colls/' + container_name
data_dict = {"id": "3", "AnimalID": "102", "Prediction": "N"}
data_dict = json.dumps(data_dict)
# family_items_to_create = ['1', 'A']

# for family_item in family_items_to_create:
#     container.create_item(body=family_item)
# insert_data = client.UpsertItem(collection_link,json.loads(data_dict)
#insert_data = container.upsert_item(json.loads(data_dict))

items = list(container.query_items(query=query, enable_cross_partition_query=True))
print(items)
request_charge = container.client_connection.last_response_headers['x-ms-request-charge']

print('Query returned {0} items. Operation consumed {1} request units'.format(len(items), request_charge))

# ------------------- Routes, acting as Controllers -----------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/joinus')
def joinus():
    return render_template('joinus.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route("/simulate", methods=['GET', 'POST'])
def simulate():
    print("In")
    return redirect(url_for('dashboard'))

@app.route("/prediction/<string:id>", methods=['GET', 'POST'])
def predict(id):
    print("id", id)
    id = "'" + id + "'"
    query = "SELECT c.Prediction FROM con_predictions c where c.AnimalID = " + id
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(items) == 0:
        result = "Invalid Cow Id"
    else:
        result = items[0]['Prediction']
        print(result)
    #return redirect(url_for('dashboard'), result)
    return render_template('dashboard_consumer.html', result=result)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() # self-defined form inheriting the FlaskForm. Records the input automatically
    print (form.email.data)
    if form.validate_on_submit(): 

        user = User.query.filter_by(email=form.email.data).first() # first user IN DB that meets this condition
        print ('true password: ', user.password)
        print ('submitted password: ', form.password.data)
        print (user.password == form.password.data)
        if user:
            print ('in the user if clause')
            if check_password_hash(user.password, form.password.data) or user.password == form.password.data:
                login_user(user, remember=form.remember.data) # from flask_login
                flash("Logged in successfully!")
                return redirect(url_for('dashboard'))

        return '<h1>Invalid email or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard_consumer.html', user=current_user)
    # else:
    #     # direct the user to the index page if something wrong happened
    #     return index()

@app.route('/signup/donor', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    print("Register form")
    if form.validate_on_submit():
        email_exists = db.session.query(User.id).filter_by(email=form.email.data).scalar() is not None

        if email_exists:
            return 'Email address already existed!'
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(
                email = form.email.data, 
                password = hashed_password,
                name = form.name.data,
                farm_address = form.farm_address.data,
                zip_code = form.zip_code.data,
                city = form.city.data,
                state = form.state.data,
                country = form.country.data,
                phone = form.phone.data,
                description = form.description.data)

            # add new user to the database
            db.session.add(new_user)
            db.session.commit()
            print("user created")
            # redirect to the login page
            return redirect(url_for('login'))
            #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup_donor.html', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user
    form = EditProfileForm()
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.farm_address = form.farm_address.data
        user.zip_code = form.zip_code.data
        user.city = form.city.data
        user.state = form.state.data
        user.country = form.country.data
        user.phone = form.phone.data
        user.description = form.description.data
        print("Profile Updated")
        return redirect(url_for('dashboard'))
    else:
        form.name.data = user.name
        form.farm_address.data = user.farm_address
        form.zip_code.data = user.zip_code
        form.city.data = user.city
        form.state.data = user.state
        form.country.data = user.country
        form.phone.data = user.phone
        form.description.data = user.description

    return render_template('edit_profile_consumer.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True) # app defined in __init__ and called when import
