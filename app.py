from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'

db = SQLAlchemy(app)


class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long = db.Column(db.String())
    short = db.Column(db.String(3))

    def __init__(self, long, short):
        self.long = long
        self.short = short


@app.before_first_request
def create_database():
    db.create_all()


def shorten_url():
    characters = string.digits + string.ascii_letters
    rand_characters = random.choices(characters, k=3)
    rand_characters = ''.join(rand_characters)
    short_url = Url.query.filter_by(short=rand_characters).first()
    if not short_url:
        return rand_characters


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_received = request.form['link']
        # CHECK IF URL ALREADY EXITS IN DATABASE
        found_url = Url.query.filter_by(long=url_received).first()
        if not found_url:
            short_url = shorten_url()
            url_data = Url(long=url_received, short=short_url)
            db.session.add(url_data)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
        else:
            # Return short url if found
            return redirect(url_for("display_short_url", url=found_url.short))
    else:
        return render_template('home.html')


@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)


@app.route('/<short_url>')
def redirection(short_url):
    converted_url = Url.query.filter_by(short=short_url).first()
    if converted_url:
        return redirect(converted_url.long)
    else:
        return f'<h1>URL does not exist</h1>'


if __name__ == '__main__':
    app.run(debug=True)
