from flask import Flask, request, redirect, render_template, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, validators
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(), nullable=False)
    short_code = db.Column(db.String(), unique=True, nullable=False)


class UrlForm(FlaskForm):
    url = StringField('URL', validators=[validators.URL(), validators.DataRequired()])


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UrlForm()
    if request.method == 'POST' and form.validate_on_submit():
        original_url = request.form['url']
        if original_url:
            short_code = generate_short_code()
            new_url = Url(original_url=original_url, short_code=short_code)
            db.session.add(new_url)
            db.session.commit()
            short_url = request.url_root + short_code
            return render_template('index.html', short_url=short_url, form=form)
    return render_template('index.html', form=form)



def generate_short_code(length=6):
    while True:
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not Url.query.filter_by(short_code=short_code).first():
            return short_code


@app.route('/<short_code>')
def redirect_url(short_code):
    url_entry = Url.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    else:
        flash('Invalid URL', 'danger')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=3434)

