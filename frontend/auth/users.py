from flask import flash, redirect, request, url_for
from flask_login import UserMixin
from src.database import db
from werkzeug.security import generate_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)


def load_user(user_id):
    query = db.session.query(User).get(user_id)
    db.session.remove()
    return query


def handle_needs_login():
    """Redirect to required page after login"""
    flash("You have to be logged in to access this page.")
    return redirect(url_for('analog.login', next=request.endpoint))
