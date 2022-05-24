from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash

from auth.users import User
from core.conf import BASE_DIR
from auth.forms import LoginForm

user_auth = Blueprint('auth', __name__,
                      template_folder=BASE_DIR / 'templates',
                      static_folder=BASE_DIR / 'static')


@user_auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if not user or not check_password_hash(
                user.password_hash, form.password.data):
            return render_template(
                'login.html', form=form, message='name or password not valid')
        login_user(user, remember=form.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(url_for(next_page))
        return redirect(url_for('analog.index'))
    return render_template('login.html', form=form)


@user_auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('analog.index'))
