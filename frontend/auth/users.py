from flask import flash, redirect, url_for, request
from flask_login import UserMixin

from src.database import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)


def load_user(user_id):
    return db.session.query(User).get(user_id)


def handle_needs_login():
    """Redirect to required page after login"""
    flash("You have to be logged in to access this page.")
    return redirect(url_for('analog.login', next=request.endpoint))
