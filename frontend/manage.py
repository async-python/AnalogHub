from app import create_app
from auth.users import User
from flask_script import Manager
from src.database import db

manager = Manager(create_app)


@manager.option('-u', '--name', dest='username', required=True)
@manager.option('-p', '--password', dest='password', required=True)
def create_superuser(username: str, password: str):
    user = User()
    user.name = username
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
