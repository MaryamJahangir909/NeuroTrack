from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os


def generate_scan_report(scan_data, patient_data, output_path):
    """
    Generate professional PDF report with MRI image included
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    # Colors
    primary_color = colors.HexColor('#1a3a5c')
    accent_color = colors.HexColor('#0077cc')
    danger_color = colors.HexColor('#cc0000')
    success_color = colors.HexColor('#00aa66')
    light_gray = colors.HexColor('#f5f5f5')
    dark_gray = colors.HexColor('#333333')
    medium_gray = colors.HexColor('#666666')

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=24,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=10,
        spaceBefore=5
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=medium_gray,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=2
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=13,
        textColor=accent_color,
        fontName='Helvetica-Bold',
        spaceBefore=15,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=dark_gray,
        fontName='Helvetica',
        spaceAfter=4,
        leading=16
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=medium_gray,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=12
    )

    content = []

    # Header
    content.append(Paragraph('NEUROTRACK', title_style))
    content.append(Spacer(1, 0.1 * inch))
    content.append(Paragraph('AI-Powered Brain Tumor Detection System', subtitle_style))
    content.append(Spacer(1, 0.05 * inch))
    content.append(Paragraph('Medical Scan Analysis Report', subtitle_style))
    content.append(Spacer(1, 0.2 * inch))
    content.append(HRFlowable(width='100%', thickness=2, color=accent_color))
    content.append(Spacer(1, 0.15 * inch))

    # Report metadata
    report_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    scan_date = scan_data.get('scan_date', 'N/A')
    report_id = 'NT-' + str(scan_data.get('id', '000')).zfill(6)

    meta_data = [
        ['Report ID:', report_id, 'Report Date:', report_date],
        ['Scan Date:', scan_date, 'System:', 'NeuroTrack v2.0']
    ]

    meta_table = Table(
        meta_data,
        colWidths=[1.2 * inch, 2.8 * inch, 1.2 * inch, 2.0 * inch]
    )
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), accent_color),
        ('TEXTCOLOR', (2, 0), (2, -1), accent_color),
        ('TEXTCOLOR', (1, 0), (1, -1), dark_gray),
        ('TEXTCOLOR', (3, 0), (3, -1), dark_gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    content.append(meta_table)
    content.append(Spacer(1, 0.15 * inch))
    content.append(HRFlowable(
        width='100%', thickness=0.5,
        color=colors.HexColor('#dddddd')
    ))

    # Patient Information
    content.append(Paragraph('PATIENT INFORMATION', section_header_style))

    patient_table_data = [
        ['Patient Name:', patient_data.get('name', 'N/A'),
         'Patient ID:', 'PT-' + str(patient_data.get('id', '000')).zfill(4)],
        ['Age:', str(patient_data.get('age', 'N/A')) + ' years',
         'Email:', patient_data.get('email', 'N/A')],
        ['Phone:', patient_data.get('phone', 'N/A') or 'Not provided',
         'Registered:', patient_data.get('created_at', 'N/A')]
    ]

    patient_table = Table(
        patient_table_data,
        colWidths=[1.2 * inch, 2.8 * inch, 1.2 * inch, 2.0 * inch]
    )
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_gray),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), accent_color),
        ('TEXTCOLOR', (2, 0), (2, -1), accent_color),
        ('TEXTCOLOR', (1, 0), (1, -1), dark_gray),
        ('TEXTCOLOR', (3, 0), (3, -1), dark_gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, colors.white])
    ]))

    content.append(patient_table)

    # MRI IMAGE SECTION
    content.append(Paragraph('MRI SCAN IMAGE', section_header_style))

    image_path = scan_data.get('image_path', '')
    heatmap_path = scan_data.get('heatmap_path', '')

    # Build image row
    image_row_content = []

    # Original MRI
    if image_path and os.path.exists(image_path):
        try:
            mri_img = Image(image_path, width=2.5 * inch, height=2.5 * inch)
            original_caption = Paragraph(
                '<b>Original MRI Scan</b>',
                ParagraphStyle('caption', parent=styles['Normal'],
                               fontSize=9, alignment=TA_CENTER,
                               textColor=dark_gray)
            )
            image_row_content.append([mri_img, original_caption])
        except Exception as e:
            print(f"Error adding MRI image: {e}")

    # Heatmap
    if heatmap_path and os.path.exists(heatmap_path):
        try:
            heat_img = Image(heatmap_path, width=2.5 * inch, height=2.5 * inch)
            heatmap_caption = Paragraph(
                '<b>AI Attention Heatmap (Grad-CAM)</b>',
                ParagraphStyle('caption', parent=styles['Normal'],
                               fontSize=9, alignment=TA_CENTER,
                               textColor=dark_gray)
            )
            image_row_content.append([heat_img, heatmap_caption])
        except Exception as e:
            print(f"Error adding heatmap: {e}")

    if image_row_content:
        if len(image_row_content) == 2:
            img_table_data = [
                [image_row_content[0][0], image_row_content[1][0]],
                [image_row_content[0][1], image_row_content[1][1]]
            ]
            img_table = Table(
                img_table_data,
                colWidths=[3.5 * inch, 3.5 * inch]
            )
        else:
            img_table_data = [
                [image_row_content[0][0]],
                [image_row_content[0][1]]
            ]
            img_table = Table(
                img_table_data,
                colWidths=[3.5 * inch]
            )

        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ]))

        content.append(img_table)
        content.append(Spacer(1, 0.1 * inch))

        content.append(Paragraph(
            'Left: Original MRI scan uploaded by patient. '
            'Right: Grad-CAM heatmap showing AI attention regions '
            '(Red = High attention/possible tumor, Blue = Normal tissue).',
            ParagraphStyle('imgNote', parent=styles['Normal'],
                           fontSize=8, textColor=medium_gray,
                           alignment=TA_CENTER, italic=True)
        ))
    else:
        content.append(Paragraph(
            'MRI scan image not available.',
            normal_style
        ))

    content.append(Spacer(1, 0.1 * inch))

    # AI Analysis Results
    content.append(Paragraph('AI ANALYSIS RESULTS', section_header_style))

    tumor_type = scan_data.get('predicted_class', 'N/A').upper()
    confidence = str(round(scan_data.get('confidence_score', 0), 2)) + '%'
    is_tumor = scan_data.get('predicted_class', '') != 'notumor'

    if is_tumor:
        result_color = danger_color
        result_text = 'TUMOR DETECTED'
        result_bg = colors.HexColor('#fff0f0')
    else:
        result_color = success_color
        result_text = 'NO TUMOR DETECTED'
        result_bg = colors.HexColor('#f0fff8')

    result_data = [
        [result_text],
        ['Prediction: ' + tumor_type],
        ['Confidence Score: ' + confidence]
    ]

    result_table = Table(result_data, colWidths=[7.2 * inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), result_bg),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, 0), result_color),
        ('TEXTCOLOR', (0, 1), (-1, -1), dark_gray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 2, result_color),
    ]))

    content.append(result_table)
    content.append(Spacer(1, 0.15 * inch))

    # Probability Breakdown
    content.append(Paragraph('DETAILED PROBABILITY ANALYSIS', section_header_style))

    probs = scan_data.get('probabilities', {})
    glioma = str(probs.get('glioma', 0)) + '%'
    meningioma = str(probs.get('meningioma', 0)) + '%'
    notumor = str(probs.get('notumor', 0)) + '%'
    pituitary = str(probs.get('pituitary', 0)) + '%'

    prob_data = [
        ['Tumor Type', 'Probability', 'Assessment'],
        ['Glioma', glioma,
         'High Risk' if float(probs.get('glioma', 0)) > 50 else 'Low Risk'],
        ['Meningioma', meningioma,
         'High Risk' if float(probs.get('meningioma', 0)) > 50 else 'Low Risk'],
        ['No Tumor', notumor,
         'Normal' if float(probs.get('notumor', 0)) > 50 else 'Abnormal'],
        ['Pituitary', pituitary,
         'High Risk' if float(probs.get('pituitary', 0)) > 50 else 'Low Risk']
    ]

    prob_table = Table(
        prob_data,
        colWidths=[2.4 * inch, 2.4 * inch, 2.4 * inch]
    )
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_gray, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('BOX', (0, 0), (-1, -1), 1, accent_color)
    ]))

    content.append(prob_table)
    content.append(Spacer(1, 0.15 * inch))

    # Doctor Recommendations
    content.append(Paragraph('DOCTOR RECOMMENDATIONS', section_header_style))

    predicted = scan_data.get('predicted_class', 'notumor')

    if predicted == 'glioma':
        urgency = 'HIGH PRIORITY - Consult immediately'
        urgency_color = danger_color
        doctors = [
            '1. Neuro-oncologist - For cancer treatment planning',
            '2. Neurosurgeon - For surgical evaluation',
            '3. Radiation Oncologist - For radiation therapy planning',
            '4. Neurologist - For neurological assessment'
        ]
        next_steps = [
            '• Schedule urgent MRI with contrast within 48 hours',
            '• Get tissue biopsy for definitive diagnosis',
            '• Complete blood panel and neurological evaluation',
            '• Discuss treatment options with multidisciplinary team'
        ]
    elif predicted == 'meningioma':
        urgency = 'MODERATE PRIORITY - Consult within 1-2 weeks'
        urgency_color = colors.HexColor('#ff8800')
        doctors = [
            '1. Neurosurgeon - Primary consultation needed',
            '2. Neurologist - For monitoring and evaluation',
            '3. Radiation Oncologist - If surgery not recommended'
        ]
        next_steps = [
            '• Schedule MRI with contrast for detailed imaging',
            '• Monitor symptoms closely',
            '• Discuss observation vs treatment options',
            '• Regular follow-up every 3-6 months'
        ]
    elif predicted == 'pituitary':
        urgency = 'MODERATE PRIORITY - Consult within 1 week'
        urgency_color = colors.HexColor('#ff8800')
        doctors = [
            '1. Endocrinologist - For hormone evaluation',
            '2. Neurosurgeon - For surgical consultation',
            '3. Ophthalmologist - To check vision field defects',
            '4. Neurologist - For neurological assessment'
        ]
        next_steps = [
            '• Complete hormonal blood tests immediately',
            '• Schedule detailed pituitary MRI',
            '• Visual field testing',
            '• Discuss medication vs surgery options'
        ]
    else:
        urgency = 'LOW PRIORITY - Routine follow-up'
        urgency_color = success_color
        doctors = [
            '1. Primary Care Physician - For routine checkup',
            '2. Neurologist - If symptoms persist'
        ]
        next_steps = [
            '• Continue regular health checkups',
            '• Maintain healthy lifestyle',
            '• Report any new neurological symptoms promptly',
            '• Follow-up MRI in 12 months if recommended'
        ]

    urgency_data = [[urgency]]
    urgency_table = Table(urgency_data, colWidths=[7.2 * inch])
    urgency_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1),
         colors.HexColor('#fff0f0') if is_tumor else colors.HexColor('#f0fff8')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), urgency_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1.5, urgency_color),
    ]))
    content.append(urgency_table)
    content.append(Spacer(1, 0.1 * inch))

    content.append(Paragraph(
        'Recommended Specialists:',
        ParagraphStyle('bold', parent=styles['Normal'],
                       fontSize=10, fontName='Helvetica-Bold',
                       textColor=dark_gray)
    ))

    for doctor in doctors:
        content.append(Paragraph(doctor, normal_style))

    content.append(Spacer(1, 0.1 * inch))

    content.append(Paragraph(
        'Recommended Next Steps:',
        ParagraphStyle('bold', parent=styles['Normal'],
                       fontSize=10, fontName='Helvetica-Bold',
                       textColor=dark_gray)
    ))

    for step in next_steps:
        content.append(Paragraph(step, normal_style))

    content.append(Spacer(1, 0.15 * inch))

    # About the Diagnosis
    content.append(Paragraph('ABOUT THE DIAGNOSIS', section_header_style))

    tumor_info = {
        'glioma': 'Glioma is a type of tumor that originates in the glial cells of the brain or spine. Glial cells support and protect nerve cells. Gliomas account for about 80% of all malignant brain tumors. Treatment options include surgery, radiation therapy, and chemotherapy. Early detection and treatment significantly improve outcomes.',
        'meningioma': 'Meningioma is a tumor that forms in the meninges, the protective membranes surrounding the brain and spinal cord. About 85% of meningiomas are benign (non-cancerous) and slow-growing. Many patients live normal lives with proper treatment. Treatment includes observation, surgery, or radiation therapy.',
        'pituitary': 'Pituitary tumors form in the pituitary gland at the base of the brain. This gland controls many hormones. Most pituitary tumors are benign and very treatable. Symptoms often include vision problems and hormonal imbalances. Treatment options include surgery through the nose, medication, or radiation.',
        'notumor': 'No tumor was detected in this MRI scan. The brain appears normal without any visible masses or abnormalities. This is a positive finding. Continue regular health monitoring as recommended by your physician.'
    }

    info_text = tumor_info.get(predicted, 'Please consult your physician for information.')
    content.append(Paragraph(info_text, normal_style))

    content.append(Spacer(1, 0.2 * inch))
    content.append(HRFlowable(
        width='100%', thickness=0.5,
        color=colors.HexColor('#dddddd')
    ))
    content.append(Spacer(1, 0.1 * inch))

    # Disclaimer
    content.append(Paragraph('MEDICAL DISCLAIMER', ParagraphStyle(
        'DisclaimerHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=medium_gray,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    )))
    content.append(Spacer(1, 0.05 * inch))
    content.append(Paragraph(
        'This report is generated by NeuroTrack AI System for informational purposes only. '
        'It is NOT a substitute for professional medical advice, diagnosis, or treatment. '
        'Always seek the advice of your physician or other qualified health provider. '
        'Never disregard professional medical advice because of something in this report.',
        disclaimer_style
    ))
    content.append(Spacer(1, 0.1 * inch))
    content.append(Paragraph(
        'Generated by NeuroTrack AI System | ' +
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        disclaimer_style
    ))

    doc.build(content)
    print(f"PDF report generated: {output_path}")
    return output_path