import re
from flask import Blueprint, request, jsonify
from models import db, Patient, ScanResult
from predictor import predictor
from chatbot import chatbot
import os
import uuid
from werkzeug.utils import secure_filename
from pdf_generator import generate_scan_report

patient_bp = Blueprint('patients', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@patient_bp.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    age = data.get('age')
    phone = data.get('phone', '').strip()

    # Validate Name
    if not name:
        return jsonify({'success': False, 'error': 'Name is required'}), 400

    if len(name) < 2:
        return jsonify({'success': False, 'error': 'Name must be at least 2 characters'}), 400

    if len(name) > 100:
        return jsonify({'success': False, 'error': 'Name is too long'}), 400

    if not re.match(r'^[a-zA-Z\s]+$', name):
        return jsonify({'success': False, 'error': 'Name must contain only letters and spaces. Numbers not allowed!'}), 400

    # Validate Email
    if not email:
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'success': False, 'error': 'Please enter a valid email address (example: john@gmail.com)'}), 400

    # Validate Age
    if age is None or age == '':
        return jsonify({'success': False, 'error': 'Age is required'}), 400

    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Age must be a number'}), 400

    if age < 1:
        return jsonify({'success': False, 'error': 'Age cannot be negative or zero!'}), 400

    if age > 120:
        return jsonify({'success': False, 'error': 'Please enter a valid age (1-120)'}), 400

    # Validate Phone (optional but if provided must be valid)
    if phone:
        cleaned_phone = phone.replace('+', '').replace('-', '').replace(' ', '')
        if not cleaned_phone.isdigit():
            return jsonify({'success': False, 'error': 'Phone number must contain only digits'}), 400
        if len(cleaned_phone) < 10 or len(cleaned_phone) > 15:
            return jsonify({'success': False, 'error': 'Phone number must be 10-15 digits'}), 400

    # Check duplicate email
    existing = Patient.query.filter_by(email=email).first()
    if existing:
        return jsonify({'success': False, 'error': 'This email is already registered!'}), 400

    # Save patient
    patient = Patient(
        name=name,
        age=age,
        email=email,
        phone=phone
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Patient {name} added successfully!',
        'patient': patient.to_dict()
    }), 201

@patient_bp.route('/api/patients', methods=['GET'])
def get_all_patients():
    patients = Patient.query.all()

    if not patients:
        return jsonify({
            'success': True,
            'message': 'No patients found',
            'patients': [],
            'total': 0
        }), 200

    return jsonify({
        'success': True,
        'total': len(patients),
        'patients': [patient.to_dict() for patient in patients]
    }), 200


@patient_bp.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404

    return jsonify({
        'success': True,
        'patient': patient.to_dict()
    }), 200

@patient_bp.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)

        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404

        # Delete all scans first
        ScanResult.query.filter_by(patient_id=patient_id).delete()

        # Then delete patient
        db.session.delete(patient)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Patient deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@patient_bp.route('/api/predict', methods=['POST'])
def predict_tumor():
    try:
        if 'mri_image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        file = request.files['mri_image']
        patient_id = request.form.get('patient_id')

        if not patient_id:
            return jsonify({'success': False, 'error': 'Patient ID required'}), 400

        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only PNG, JPG, JPEG allowed'}), 400

        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '_' + filename
        upload_folder = 'uploads'
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        result = predictor.predict(file_path)

        if result.get('error'):
            os.remove(file_path)
            return jsonify({
                'success': False,
                'error': result['message']
            }), 400

        scan = ScanResult(
            patient_id=patient_id,
            image_filename=unique_filename,
            image_path=file_path,
            predicted_class=result['predicted_class'],
            confidence_score=result['confidence'],
            glioma_prob=result['probabilities']['glioma'],
            meningioma_prob=result['probabilities']['meningioma'],
            notumor_prob=result['probabilities']['notumor'],
            pituitary_prob=result['probabilities']['pituitary']
        )

        db.session.add(scan)
        db.session.commit()

        heatmap_base64 = None
        try:
            class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
            class_index = class_names.index(result['predicted_class'])

            heatmap_result = predictor.gradcam.save_heatmap(
                file_path,
                class_index,
                scan.id
            )

            if heatmap_result:
                heatmap_base64 = heatmap_result['base64']
                print("Heatmap generated for scan " + str(scan.id))

        except Exception as heatmap_error:
            print("Heatmap generation failed: " + str(heatmap_error))
            heatmap_base64 = None

        return jsonify({
            'success': True,
            'scan_id': scan.id,
            'patient_name': patient.name,
            'heatmap': heatmap_base64,
            'prediction': {
                'tumor_type': result['predicted_class'],
                'confidence': round(result['confidence'] * 100, 2),
                'is_tumor': result['is_tumor'],
                'probabilities': {
                    k: round(v * 100, 2)
                    for k, v in result['probabilities'].items()
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@patient_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    total_scans = ScanResult.query.count()
    total_patients = Patient.query.count()
    tumor_detected = ScanResult.query.filter(
        ScanResult.predicted_class != 'notumor'
    ).count()
    no_tumor = ScanResult.query.filter_by(
        predicted_class='notumor'
    ).count()
    glioma = ScanResult.query.filter_by(
        predicted_class='glioma'
    ).count()
    meningioma = ScanResult.query.filter_by(
        predicted_class='meningioma'
    ).count()
    pituitary = ScanResult.query.filter_by(
        predicted_class='pituitary'
    ).count()

    recent_scans = ScanResult.query.order_by(
        ScanResult.scan_date.desc()
    ).limit(5).all()

    return jsonify({
        'success': True,
        'stats': {
            'total_scans': total_scans,
            'total_patients': total_patients,
            'tumor_detected': tumor_detected,
            'no_tumor': no_tumor,
            'glioma': glioma,
            'meningioma': meningioma,
            'pituitary': pituitary
        },
        'recent_scans': [scan.to_dict() for scan in recent_scans]
    }), 200


@patient_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()

        if not data or not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400

        user_message = data['message'].strip()
        patient_id = data.get('patient_id', None)
        session_id = data.get('session_id', 'default')

        result = chatbot.generate_response(
            user_message,
            patient_id,
            session_id
        )

        return jsonify({
            'success': True,
            'response': result['response'],
            'intent': result['intent']
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@patient_bp.route('/api/report/<int:scan_id>', methods=['GET'])
def download_report(scan_id):
    try:
        scan = ScanResult.query.get(scan_id)
        if not scan:
            return jsonify({'success': False, 'error': 'Scan not found'}), 404

        patient = Patient.query.get(scan.patient_id)
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404

        # Get heatmap path
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        heatmap_path = os.path.join(
            BASE_DIR, 'uploads', 'heatmaps',
            f'heatmap_{scan_id}.jpg'
        )

        scan_data = {
            'id': scan.id,
            'predicted_class': scan.predicted_class,
            'confidence_score': round(scan.confidence_score * 100, 2),
            'scan_date': scan.scan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'image_path': os.path.join(BASE_DIR, scan.image_path),
            'heatmap_path': heatmap_path if os.path.exists(heatmap_path) else '',
            'probabilities': {
                'glioma': round(scan.glioma_prob * 100, 2),
                'meningioma': round(scan.meningioma_prob * 100, 2),
                'notumor': round(scan.notumor_prob * 100, 2),
                'pituitary': round(scan.pituitary_prob * 100, 2)
            }
        }

        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'email': patient.email,
            'phone': patient.phone,
            'created_at': patient.created_at.strftime('%Y-%m-%d')
        }

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_folder = os.path.join(BASE_DIR, 'uploads', 'reports')
        os.makedirs(reports_folder, exist_ok=True)

        pdf_filename = f'report_scan_{scan_id}.pdf'
        pdf_path = os.path.join(reports_folder, pdf_filename)

        generate_scan_report(scan_data, patient_data, pdf_path)

        from flask import send_file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'NeuroTrack_Report_{patient.name}_{scan_id}.pdf'
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500