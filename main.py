from flask import Flask
from application.models import db
from application.models import *


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quiz_master.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app) # flask app connected to db(SQL alchemy)

    with app.app_context():
        db.session.rollback()
        db.drop_all()
        db.create_all()
        from upload_data import upload_data
        upload_data()
    app.app_context().push()
    return app

app = create_app()  

from application.controllers import *

if __name__ == "__main__":
    app.run(debug=True)