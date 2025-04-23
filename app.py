from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from flask_migrate import Migrate
import os

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Enregistrement des blueprints
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.vehicles import vehicles_bp
    from routes.drivers import drivers_bp
    from routes.trips import trips_bp
    from routes.finances import finances_bp
    from routes.dashboard import dashboard_bp
    from routes.events import events_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(finances_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    
    # Création des dossiers nécessaires
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Initialiser la base de données avec un utilisateur admin si elle est vide
    @app.before_first_request
    def create_initial_user():
        with app.app_context():
            db.create_all()
            if not User.query.filter_by(username='admin.admin').first():
                admin = User(
                    nom='Admin',
                    prenom='Admin',
                    username='admin.admin',
                    role='admin'
                )
                admin.set_password('admin.admin')
                db.session.add(admin)
                db.session.commit()
    
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
