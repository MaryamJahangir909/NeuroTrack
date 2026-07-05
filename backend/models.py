from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User accounts for doctors and patients"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    age = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'age': self.age,
            'phone': self.phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Patient(db.Model):
    """Store patient information"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scans = db.relationship('ScanResult', backref='patient', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class ScanResult(db.Model):
    """Store MRI scan results"""
    __tablename__ = 'scan_results'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey('patients.id'),
        nullable=False
    )
    image_filename = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    predicted_class = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)

    glioma_prob = db.Column(db.Float, default=0.0)
    meningioma_prob = db.Column(db.Float, default=0.0)
    notumor_prob = db.Column(db.Float, default=0.0)
    pituitary_prob = db.Column(db.Float, default=0.0)

    heatmap_path = db.Column(db.String(255), nullable=True)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name,
            'image_filename': self.image_filename,
            'predicted_class': self.predicted_class,
            'confidence_score': round(self.confidence_score * 100, 2),
            'probabilities': {
                'glioma': round(self.glioma_prob * 100, 2),
                'meningioma': round(self.meningioma_prob * 100, 2),
                'notumor': round(self.notumor_prob * 100, 2),
                'pituitary': round(self.pituitary_prob * 100, 2)
            },
            'heatmap_path': self.heatmap_path,
            'scan_date': self.scan_date.strftime('%Y-%m-%d %H:%M:%S')
        }