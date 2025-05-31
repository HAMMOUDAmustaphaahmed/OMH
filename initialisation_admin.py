from flask import Flask
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    admin = User.query.filter_by(username='admin.admin').first()
    if admin:
        admin.set_password('admin.admin')
        db.session.commit()
        print("Mot de passe admin réinitialisé avec succès!")