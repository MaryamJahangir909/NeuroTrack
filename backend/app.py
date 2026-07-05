from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes import patient_bp
from auth import auth_bp
import os

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = 'neurotrack-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neurotrack.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['JWT_SECRET_KEY'] = 'neurotrack-jwt-secret-2024'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    JWTManager(app)

    # Register blueprints
    app.register_blueprint(patient_bp)
    app.register_blueprint(auth_bp)

    # Create upload folders
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('uploads/heatmaps', exist_ok=True)

    return app


app = create_app()


@app.route('/')
def home():
    return {
        'message': 'NeuroTrack API is running!',
        'status': 'success',
        'version': '2.0'
    }


@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'database': 'connected',
        'auth': 'enabled'
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully")

    print("🚀 NeuroTrack Backend Running on http://localhost:5000")
    app.run(debug=True, port=5000)