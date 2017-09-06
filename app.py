#!/usr/bin/env python3

"""
https://flask-mongoengine.readthedocs.io/en/latest/
"""

from flask import Flask, render_template, redirect, url_for, request
from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form
from wtforms import validators

db = MongoEngine()

class User(db.Document):
    email = db.StringField(required=True, max_length=255)
    first_name = db.StringField(max_length=10)
    last_name = db.StringField(max_length=10)

    def __str__(self):
        return self.email


class Content(db.EmbeddedDocument):
    text = db.StringField()
    lang = db.StringField(max_length=3)


class Post(db.Document):
    internal = db.StringField()
    author = db.ReferenceField(User)
    title = db.StringField(max_length=10, required=True, validators=[validators.InputRequired(message=u'Missing title.'),])
    tags = db.ListField(db.StringField(max_length=30))
    content = db.EmbeddedDocumentField(Content)

app = Flask(__name__)
app.config['MONGODB_DB'] = 'flask_mongoengine_example'
app.config['WTF_CSRF_SECRET_KEY'] = b'\x00.fQa\xea\x97\xc1\xcf\xf8\xb0\x91\x90\xe9\xb9\xfe\xb2\xe6\xf2rS\xb9\x124'
app.secret_key = 'a\x82\xb6F\x98\xab+\x07\\R\xd8\x1f\xd9\xc7\xfd\x88/\xa6.\xcc\x98\x1aa\x0e'
db.init_app(app)


@app.route("/")
def hello():
    return render_template('index.html', posts=Post.objects, users=User.objects)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):

    post = Post.objects.get_or_404(id=post_id)

    PostForm = model_form(Post, exclude=['internal'])
    form = PostForm(request.form, obj=post)

    if form.validate_on_submit():
        form.save()

        return redirect(url_for('hello'))

    return render_template('edit_post.html', post=post, form=form)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():

    PostForm = model_form(Post, exclude=['internal'])
    form = PostForm(request.form)

    if form.validate_on_submit():

        data = form.data.copy()
        data.pop('csrf_token', None)
        data['content'].pop('csrf_token', None)
        form.model_class(**data).save()
        # form.save()

        return redirect(url_for('hello'))

    return render_template('add_post.html', form=form)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():

    UserForm = model_form(User)
    form = UserForm(request.form)

    if form.validate_on_submit():

        data = form.data.copy()
        data.pop('csrf_token', None)
        form.model_class(**data).save()
        # form.save()

        return redirect(url_for('hello'))

    return render_template('add_user.html', form=form)

app.run()
