import random
import re
import difflib
from models import db, ScanResult

class NeuroTrackChatbot:
    def __init__(self):
        self.used_responses = {}

        self.knowledge_base = {
            'glioma': {
                'definition': 'Glioma is a type of brain tumor that develops from glial cells, which are the supportive cells surrounding and protecting neurons in the brain and spinal cord. Gliomas account for about 80% of all malignant brain tumors.',
                'types': 'There are several types of gliomas: Astrocytomas (from star-shaped cells), Oligodendrogliomas (from myelin-producing cells), Ependymomas (from cells lining brain ventricles), and Glioblastoma (most aggressive, Grade 4).',
                'symptoms': 'Common symptoms include persistent headaches that worsen over time, new-onset seizures, memory loss, personality or behavior changes, vision problems, difficulty speaking, weakness on one side of the body, and nausea with vomiting.',
                'treatment': 'Treatment depends on grade and location. Options include surgical removal, radiation therapy, chemotherapy (Temozolomide is common), targeted drug therapy, and clinical trials. A combination approach is often used.',
                'prognosis': 'Prognosis varies significantly by grade. Low-grade (Grade 1-2) gliomas may have 5-10+ year survival. Anaplastic (Grade 3) has 2-5 year survival. Glioblastoma (Grade 4) has median survival of 12-18 months with treatment. Early detection is crucial.'
            },
            'meningioma': {
                'definition': 'Meningioma is a tumor that forms in the meninges, which are the three protective membranes covering the brain and spinal cord. About 85% of meningiomas are benign (non-cancerous) and grow slowly over years.',
                'types': 'Meningiomas are graded as: Grade 1 (Benign - 80% of cases, slow growing), Grade 2 (Atypical - faster growing, may recur), Grade 3 (Anaplastic/Malignant - rare, aggressive). Location also matters: convexity, parasagittal, sphenoid wing, olfactory groove.',
                'symptoms': 'Symptoms develop gradually and include headaches that worsen over time, vision changes or blurriness, hearing loss or ringing in ears, memory problems, seizures, weakness in arms or legs, and personality changes.',
                'treatment': 'Treatment options include active surveillance with regular MRI for small tumors, surgical removal for larger or symptomatic tumors, stereotactic radiosurgery (Gamma Knife), and conventional radiation therapy. Many benign meningiomas need only monitoring.',
                'prognosis': 'Prognosis is generally excellent. The 5-year survival rate is around 84%. Most patients with benign meningiomas live normal lives after treatment. Recurrence is possible but usually manageable. Regular follow-up MRI is recommended.'
            },
            'pituitary': {
                'definition': 'Pituitary tumors develop in the pituitary gland, a small pea-sized gland at the base of the brain. This gland is the master controller of hormones, regulating thyroid, adrenal glands, growth, and reproduction.',
                'types': 'Two main categories: Functioning tumors (produce excess hormones like prolactinoma, growth hormone-secreting, ACTH-secreting) and Non-functioning tumors (do not produce hormones but press on nearby structures causing symptoms).',
                'symptoms': 'Symptoms include vision problems especially peripheral vision loss, headaches, hormonal imbalances causing fatigue, unexplained weight gain or loss, irregular menstrual periods, decreased libido, and in some cases milk production without pregnancy.',
                'treatment': 'Treatment includes transsphenoidal surgery (minimally invasive through the nose), medications like Cabergoline or Bromocriptine for prolactinomas, radiation therapy, and hormone replacement therapy if the gland is damaged.',
                'prognosis': 'Excellent prognosis with over 97% five-year survival rate. Most pituitary tumors are benign and completely treatable. Patients typically return to normal life with proper treatment. Hormone function usually recovers.'
            },
            'notumor': {
                'definition': 'A "No Tumor" result means the AI did not detect any abnormal growth or mass in the brain MRI scan. The brain structures appear normal without visible tumors.',
                'advice': 'Even with a clear scan, maintain regular health checkups. Report any new or persistent neurological symptoms to your doctor. Maintain a healthy lifestyle with proper diet, regular exercise, adequate sleep, and stress management.'
            }
        }

    def get_scan_from_db(self, patient_id=None):
        try:
            if patient_id:
                scan = ScanResult.query.filter_by(
                    patient_id=patient_id
                ).order_by(ScanResult.scan_date.desc()).first()
            else:
                scan = ScanResult.query.order_by(
                    ScanResult.scan_date.desc()
                ).first()
            if scan:
                return {
                    'found': True,
                    'patient': scan.patient.name,
                    'prediction': scan.predicted_class,
                    'confidence': round(scan.confidence_score * 100, 2),
                    'date': scan.scan_date.strftime('%Y-%m-%d'),
                    'glioma': round(scan.glioma_prob * 100, 2),
                    'meningioma': round(scan.meningioma_prob * 100, 2),
                    'notumor': round(scan.notumor_prob * 100, 2),
                    'pituitary': round(scan.pituitary_prob * 100, 2)
                }
            return {'found': False}
        except:
            return {'found': False}

    def fuzzy_match(self, word, targets, threshold=0.7):
        for target in targets:
            if difflib.SequenceMatcher(None, word.lower(), target.lower()).ratio() >= threshold:
                return target
        return None

    def detect_intent(self, message):
        msg = message.lower().strip()
        words = re.findall(r'\w+', msg)

        intent_scores = {
            'greeting': 0, 'farewell': 0, 'thanks': 0,
            'scan_result': 0, 'upload_guide': 0, 'dashboard_guide': 0,
            'result_explain': 0, 'confidence_explain': 0,
            'glioma': 0, 'meningioma': 0, 'pituitary': 0,
            'symptoms': 0, 'treatment': 0, 'prevention': 0,
            'doctor': 0, 'mri_info': 0, 'about_neurotrack': 0,
            'tumor_general': 0, 'prognosis': 0, 'joke': 0,
            'how_are_you': 0, 'name': 0, 'capabilities': 0
        }

        greet_words = ['hello', 'hi', 'hey', 'hii', 'helo', 'hai', 'salam', 'assalam', 'greetings', 'good morning', 'good evening']
        farewell_words = ['bye', 'goodbye', 'see you', 'take care', 'cya', 'see ya', 'later', 'quit', 'exit']
        thanks_words = ['thank', 'thanks', 'thx', 'thankyou', 'appreciate', 'grateful']
        scan_words = ['my result', 'my scan', 'show my', 'scan result', 'my report', 'my prediction', 'my mri', 'what did my']
        upload_words = ['upload', 'how to upload', 'upload mri', 'upload image', 'upload scan', 'submit']
        dashboard_words = ['dashboard', 'statistics', 'stats', 'charts', 'analytics', 'overview']
        result_words = ['what does this mean', 'result mean', 'explain result', 'interpret', 'what is this result', 'understand result']
        confidence_words = ['confidence', 'confidence score', 'how confident', 'accuracy', 'how accurate', 'percentage']
        glioma_words = ['glioma', 'glioblastoma', 'astrocytoma', 'oligodendroglioma', 'ependymoma']
        meningioma_words = ['meningioma', 'meningeal', 'meninges tumor']
        pituitary_words = ['pituitary', 'pituitary tumor', 'pituitary adenoma']
        symptom_words = ['symptom', 'symptoms', 'sign', 'signs', 'feel', 'feeling', 'headache', 'dizzy', 'seizure', 'nausea', 'vomit', 'pain', 'vision problem', 'memory loss']
        treatment_words = ['treatment', 'treat', 'cure', 'surgery', 'therapy', 'chemo', 'radiation', 'medicine', 'medication', 'operation']
        prevention_words = ['prevent', 'prevention', 'avoid', 'protect', 'reduce risk', 'lower risk', 'safe']
        doctor_words = ['doctor', 'specialist', 'neurologist', 'neurosurgeon', 'oncologist', 'consult', 'hospital', 'appointment']
        mri_words = ['mri', 'magnetic resonance', 'imaging', 'scan', 'mri scan']
        about_words = ['neurotrack', 'this app', 'this system', 'this website', 'about this', 'what is this', 'about neurotrack']
        tumor_words = ['brain tumor', 'brain tumour', 'brain cancer', 'tumor', 'tumour', 'brain growth']
        prognosis_words = ['prognosis', 'survival', 'chance', 'life expectancy', 'how long', 'survive', 'fatal', 'dangerous']
        joke_words = ['joke', 'funny', 'laugh', 'humor', 'fun', 'comedy']
        how_words = ['how are you', 'how r u', 'hows you', 'you good', 'you okay']
        name_words = ['your name', 'who are you', 'what are you', 'introduce']
        cap_words = ['what can you do', 'capabilities', 'help me', 'how can you help', 'what do you know']

        def score_category(category, keywords, weight=1):
            for kw in keywords:
                if kw in msg:
                    intent_scores[category] += weight * len(kw)
            for word in words:
                match = self.fuzzy_match(word, keywords, 0.75)
                if match:
                    intent_scores[category] += weight * 0.5

        score_category('greeting', greet_words, 2)
        score_category('farewell', farewell_words, 2)
        score_category('thanks', thanks_words, 2)
        score_category('scan_result', scan_words, 3)
        score_category('upload_guide', upload_words, 2)
        score_category('dashboard_guide', dashboard_words, 2)
        score_category('result_explain', result_words, 3)
        score_category('confidence_explain', confidence_words, 2)
        score_category('glioma', glioma_words, 3)
        score_category('meningioma', meningioma_words, 3)
        score_category('pituitary', pituitary_words, 3)
        score_category('symptoms', symptom_words, 2)
        score_category('treatment', treatment_words, 2)
        score_category('prevention', prevention_words, 2)
        score_category('doctor', doctor_words, 2)
        score_category('mri_info', mri_words, 2)
        score_category('about_neurotrack', about_words, 3)
        score_category('tumor_general', tumor_words, 2)
        score_category('prognosis', prognosis_words, 2)
        score_category('joke', joke_words, 2)
        score_category('how_are_you', how_words, 2)
        score_category('name', name_words, 2)
        score_category('capabilities', cap_words, 2)

        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]

        if best_score > 0:
            sub_intent = None
            for tumor in ['glioma', 'meningioma', 'pituitary']:
                if intent_scores[tumor] > 0:
                    sub_intent = tumor
                    break

            if best_intent in ['symptoms', 'treatment', 'prognosis'] and sub_intent:
                return best_intent, sub_intent

            return best_intent, None

        return 'unknown', None

    def get_varied_response(self, category, responses):
        if category not in self.used_responses:
            self.used_responses[category] = []

        available = [r for i, r in enumerate(responses) if i not in self.used_responses[category]]

        if not available:
            self.used_responses[category] = []
            available = responses

        chosen = random.choice(available)
        idx = responses.index(chosen)
        self.used_responses[category].append(idx)

        return chosen

    def generate_response(self, user_message, patient_id=None, session_id="default"):
        intent, sub_tumor = self.detect_intent(user_message)
        response = self.build_response(intent, sub_tumor, user_message, patient_id)
        return {'response': response, 'intent': intent}

    def build_response(self, intent, sub_tumor, message, patient_id):
        msg = message.lower().strip()

        # ===== GREETINGS =====
        if intent == 'greeting':
            responses = [
                "Hey there! Welcome to NeuroTrack. I am your AI medical assistant. How can I help you today?",
                "Hello! Great to see you here. I can help you understand brain tumors, guide you through the system, or answer medical questions. What would you like to know?",
                "Hi! I am Assistant, your NeuroTrack guide. Whether you need help uploading an MRI, understanding results, or learning about brain health, I am here for you!",
                "Welcome to NeuroTrack! I am your virtual assistant. Feel free to ask me anything about brain tumors, our system, or your scan results."
            ]
            return self.get_varied_response('greeting', responses)

        # ===== HOW ARE YOU =====
        if intent == 'how_are_you':
            responses = [
                "I am doing great, thank you for asking! I am always ready to help you with brain health questions. How are YOU feeling today?",
                "Wonderful, thanks for checking in! I love helping people understand their brain health. What can I assist you with?",
                "I am fantastic and ready to help! What brings you to NeuroTrack today?"
            ]
            return self.get_varied_response('how_are_you', responses)

        # ===== THANKS =====
        if intent == 'thanks':
            responses = [
                "You are most welcome! I am always here whenever you need help. Take care of yourself!",
                "Happy to help! Do not hesitate to ask if you have more questions. Your health matters!",
                "Glad I could assist you! Remember, early detection saves lives. Feel free to come back anytime!"
            ]
            return self.get_varied_response('thanks', responses)

        # ===== FAREWELL =====
        if intent == 'farewell':
            responses = [
                "Goodbye! Take care of yourself and stay healthy. Remember to keep up with regular checkups. See you next time!",
                "See you! Wishing you good health. If you ever have questions about brain health, I am always here to help!",
                "Bye! It was great assisting you. Stay well and do not forget your follow-up appointments!"
            ]
            return self.get_varied_response('farewell', responses)

        # ===== JOKES =====
        if intent == 'joke':
            jokes = [
                "Why did the neuron break up with the synapse? Because it felt there was no connection! Hope that brought a smile. Now, can I help with something medical?",
                "What did the brain say to the heart during an argument? Stop overreacting! Just a bit of medical humor. What would you like to know?",
                "Why was the brain so good at poker? It always had a lot going on inside! Now seriously, how can I help you with brain health?",
                "What do you call a brain that will not stop talking? A real no-brainer! Okay, back to business. Any medical questions?"
            ]
            return random.choice(jokes)

        # ===== NAME =====
        if intent == 'name':
            return "I am Assistant, the AI guide built into NeuroTrack. I am designed to help you understand brain tumors, navigate our system, interpret scan results, and provide medical awareness. Think of me as your personal medical information guide!"

        # ===== CAPABILITIES =====
        if intent == 'capabilities':
            return "Here is everything I can help you with:\n\n**System Guide:**\n- How to upload MRI scans\n- How to use the dashboard\n- How to interpret your results\n- What confidence scores mean\n\n**Medical Knowledge:**\n- Brain tumor types (Glioma, Meningioma, Pituitary)\n- Symptoms and warning signs\n- Treatment options\n- Prevention tips\n- When to see a doctor\n\n**Your Data:**\n- Show your latest scan results\n- Explain your specific prediction\n\nJust ask naturally, like you would ask a real assistant!"

        # ===== ABOUT NEUROTRACK =====
        if intent == 'about_neurotrack':
            responses = [
                "**NeuroTrack** is an AI-powered Brain Tumor Detection System built to help patients and doctors.\n\n**What it does:**\nUpload a brain MRI scan and our AI instantly analyzes it to detect tumors with 92.77% accuracy.\n\n**Key Features:**\n- AI tumor classification (Glioma, Meningioma, Pituitary)\n- Grad-CAM heatmap showing exactly where tumor is\n- Professional PDF medical reports\n- Real-time analytics dashboard\n- Secure patient management\n- AI medical assistant (that is me!)\n\n**Technology:**\nBuilt with deep learning (MobileNetV2 CNN), trained on 5,600 real MRI images from medical databases.\n\nWould you like to know how to use any specific feature?",
                "NeuroTrack is a complete brain tumor screening platform. It uses artificial intelligence to analyze brain MRI scans and detect three types of tumors: Glioma, Meningioma, and Pituitary tumors.\n\nThe system provides instant predictions with confidence scores, visual heatmaps showing tumor locations, and downloadable PDF reports that you can share with your doctor.\n\nIt is designed to be a first-line screening tool that helps with early detection. What would you like to explore?"
            ]
            return self.get_varied_response('about', responses)

        # ===== UPLOAD GUIDE =====
        if intent == 'upload_guide':
            return "**How to Upload an MRI Scan:**\n\n**Step 1:** Click on 'Upload MRI' in the navigation bar\n\n**Step 2:** Select an existing patient from the dropdown, or add a new patient by filling in their name, age, and email\n\n**Step 3:** Click the upload area and select your brain MRI image file (JPG, JPEG, or PNG format)\n\n**Step 4:** Click the 'Analyze MRI' button\n\n**Step 5:** Wait a few seconds while our AI analyzes the scan\n\n**Step 6:** View your results including:\n- Tumor classification\n- Confidence score\n- Probability breakdown for all types\n- Grad-CAM heatmap visualization\n\n**Step 7:** Click 'Download PDF Report' to get a professional medical report\n\nNeed help with any specific step?"

        # ===== DASHBOARD GUIDE =====
        if intent == 'dashboard_guide':
            return "**Understanding the Dashboard:**\n\nThe Dashboard gives you a complete overview of all activity in NeuroTrack.\n\n**Statistics Cards:**\n- Total Scans: Number of MRIs analyzed\n- Total Patients: Registered patients\n- Tumors Detected: Scans showing tumors\n- No Tumor: Healthy scan results\n\n**Charts:**\n- Tumor Distribution: Pie chart showing breakdown by type\n- Scan Overview: Bar chart comparing categories\n\n**Recent Scans Table:**\nShows the 5 most recent scans with patient name, prediction, confidence, date, and status.\n\n**Registered Patients:**\nLists all patients in the system with their details.\n\nAll data updates in real-time as new scans are performed!"

        # ===== RESULT EXPLANATION =====
        if intent == 'result_explain':
            return "**Understanding Your Results:**\n\n**Prediction:** This is the tumor type our AI identified. It can be:\n- **Glioma:** Tumor from glial cells\n- **Meningioma:** Tumor from brain membranes\n- **Pituitary:** Tumor from pituitary gland\n- **No Tumor:** Healthy brain\n\n**Confidence Score:** Shows how certain the AI is about its prediction. Higher percentage means more confident.\n\n**Probabilities:** Shows the AI's assessment for ALL four categories. The highest one is the prediction.\n\n**Heatmap:** The colored overlay on your MRI shows which areas the AI focused on. Red areas influenced the decision most.\n\n**Important:** AI results are screening tools. Always confirm with a qualified doctor before making treatment decisions."

        # ===== CONFIDENCE EXPLANATION =====
        if intent == 'confidence_explain':
            return "**What Does Confidence Score Mean?**\n\nThe confidence score tells you how certain our AI model is about its prediction.\n\n**How to interpret it:**\n- **95-100%:** Very high confidence. AI is almost certain.\n- **85-94%:** High confidence. Strong prediction.\n- **70-84%:** Moderate confidence. Consider getting a second opinion.\n- **Below 70%:** Low confidence. Definitely consult a doctor.\n\n**How it is calculated:**\nOur CNN model outputs probabilities for all 4 classes. The confidence score is the probability of the predicted class.\n\n**Example:**\nIf Glioma = 94%, Meningioma = 3%, No Tumor = 2%, Pituitary = 1%\nThen Prediction = Glioma with 94% confidence.\n\nOur model achieves 92.77% overall accuracy on test data."

        # ===== SCAN RESULTS =====
        if intent == 'scan_result':
            scan = self.get_scan_from_db(patient_id)
            if scan['found']:
                pred = scan['prediction']
                conf = scan['confidence']
                name = scan['patient']
                date = scan['date']

                response = f"Here are the latest scan results for **{name}**:\n\n"
                response += f"**Prediction:** {pred.upper()}\n"
                response += f"**Confidence:** {conf}%\n"
                response += f"**Scan Date:** {date}\n\n"
                response += f"**Detailed Probabilities:**\n"
                response += f"- Glioma: {scan['glioma']}%\n"
                response += f"- Meningioma: {scan['meningioma']}%\n"
                response += f"- No Tumor: {scan['notumor']}%\n"
                response += f"- Pituitary: {scan['pituitary']}%\n\n"

                if pred == 'notumor':
                    response += "Good news! No tumor was detected. The AI is " + str(conf) + "% confident about this result. Continue with regular health checkups as recommended."
                elif pred == 'glioma':
                    response += "The scan indicates signs of **Glioma** with " + str(conf) + "% confidence. This requires medical attention. I recommend consulting a neuro-oncologist promptly for further evaluation."
                elif pred == 'meningioma':
                    response += "The scan indicates signs of **Meningioma** with " + str(conf) + "% confidence. Most meningiomas are benign, but please consult a neurosurgeon for proper evaluation and monitoring."
                elif pred == 'pituitary':
                    response += "The scan indicates signs of a **Pituitary tumor** with " + str(conf) + "% confidence. Please consult an endocrinologist or neurosurgeon for hormone evaluation and treatment planning."

                response += "\n\nWould you like me to explain what this means in more detail, or help you understand treatment options?"
                return response
            else:
                return "I could not find any scan results yet. To get your results:\n\n1. Go to the **Upload MRI** page\n2. Add or select a patient\n3. Upload your brain MRI image\n4. Click **Analyze MRI**\n\nOnce analyzed, come back and ask me to show your results!"

        # ===== GLIOMA =====
        if intent == 'glioma' or (sub_tumor == 'glioma' and intent in ['symptoms', 'treatment', 'prognosis']):
            info = self.knowledge_base['glioma']
            if intent == 'symptoms' or 'symptom' in msg:
                return f"**Glioma - Symptoms:**\n\n{info['symptoms']}\n\nIf you or someone you know is experiencing these symptoms, please consult a neurologist. Early detection significantly improves outcomes.\n\nWould you like to know about treatment options?"
            elif intent == 'treatment' or 'treat' in msg:
                return f"**Glioma - Treatment Options:**\n\n{info['treatment']}\n\nTreatment is personalized based on tumor grade, location, and patient health. A multidisciplinary team including neurosurgeon, oncologist, and radiologist will create the best plan.\n\nWould you like to know about prognosis?"
            elif intent == 'prognosis' or any(w in msg for w in ['prognosis', 'survival', 'chance']):
                return f"**Glioma - Prognosis:**\n\n{info['prognosis']}\n\nRemember, statistics are averages. Individual outcomes vary greatly based on many factors. Always discuss specific prognosis with your medical team."
            else:
                return f"**About Glioma:**\n\n{info['definition']}\n\n**Types:** {info['types']}\n\nYou can ask me specifically about:\n- Glioma symptoms\n- Glioma treatment\n- Glioma prognosis\n\nWhat would you like to know more about?"

        # ===== MENINGIOMA =====
        if intent == 'meningioma' or (sub_tumor == 'meningioma' and intent in ['symptoms', 'treatment', 'prognosis']):
            info = self.knowledge_base['meningioma']
            if intent == 'symptoms' or 'symptom' in msg:
                return f"**Meningioma - Symptoms:**\n\n{info['symptoms']}\n\nSince meningiomas grow slowly, symptoms often develop gradually over months or years. Regular checkups help catch them early.\n\nWould you like to know about treatment?"
            elif intent == 'treatment' or 'treat' in msg:
                return f"**Meningioma - Treatment Options:**\n\n{info['treatment']}\n\nMany small meningiomas do not need immediate treatment and are monitored with regular MRI scans.\n\nWant to know about prognosis?"
            elif intent == 'prognosis' or any(w in msg for w in ['prognosis', 'survival', 'chance']):
                return f"**Meningioma - Prognosis:**\n\n{info['prognosis']}\n\nThe outlook for meningioma patients is generally very positive, especially for Grade 1 tumors."
            else:
                return f"**About Meningioma:**\n\n{info['definition']}\n\n**Grades:** {info['types']}\n\nAsk me about:\n- Meningioma symptoms\n- Meningioma treatment\n- Meningioma prognosis"

        # ===== PITUITARY =====
        if intent == 'pituitary' or (sub_tumor == 'pituitary' and intent in ['symptoms', 'treatment', 'prognosis']):
            info = self.knowledge_base['pituitary']
            if intent == 'symptoms' or 'symptom' in msg:
                return f"**Pituitary Tumor - Symptoms:**\n\n{info['symptoms']}\n\nSince the pituitary gland controls hormones, these tumors can cause wide-ranging symptoms throughout the body.\n\nWould you like to know about treatment?"
            elif intent == 'treatment' or 'treat' in msg:
                return f"**Pituitary Tumor - Treatment Options:**\n\n{info['treatment']}\n\nThe choice of treatment depends on tumor type, size, and whether it produces hormones.\n\nWant to know about prognosis?"
            elif intent == 'prognosis' or any(w in msg for w in ['prognosis', 'survival', 'chance']):
                return f"**Pituitary Tumor - Prognosis:**\n\n{info['prognosis']}\n\nMost patients with pituitary tumors have excellent long-term outcomes."
            else:
                return f"**About Pituitary Tumors:**\n\n{info['definition']}\n\n**Types:** {info['types']}\n\nAsk me about:\n- Pituitary symptoms\n- Pituitary treatment\n- Pituitary prognosis"

        # ===== SYMPTOMS (General) =====
        if intent == 'symptoms':
            responses = [
                "**Common Brain Tumor Symptoms:**\n\n- Persistent headaches (especially worse in morning)\n- New onset seizures\n- Vision problems (blurriness, double vision, peripheral loss)\n- Hearing loss or ringing in ears\n- Balance and coordination difficulties\n- Memory loss or confusion\n- Personality or behavior changes\n- Nausea and vomiting (unexplained)\n- Weakness or numbness in limbs\n- Speech difficulties\n\n**Important:** These symptoms can be caused by many conditions, not just tumors. However, if you experience persistent or worsening symptoms, please consult a neurologist promptly.\n\nWould you like to know about symptoms of a specific tumor type?",
                "**Warning Signs to Watch For:**\n\nBrain tumor symptoms vary by location and size, but common ones include:\n\n1. **Headaches** that progressively worsen and do not respond to usual medication\n2. **Seizures** in someone with no history of seizures\n3. **Vision changes** like blurriness or loss of peripheral vision\n4. **Cognitive changes** including memory problems and confusion\n5. **Motor issues** like weakness on one side or balance problems\n\nEarly detection saves lives. If you have concerns, do not delay seeing a doctor.\n\nWant details about a specific tumor type?"
            ]
            return self.get_varied_response('symptoms', responses)

        # ===== TREATMENT (General) =====
        if intent == 'treatment':
            return "**Brain Tumor Treatment Options:**\n\n**1. Surgery**\nGoal is to remove as much tumor as safely possible. Advanced techniques include awake craniotomy and intraoperative MRI guidance.\n\n**2. Radiation Therapy**\nUses high-energy rays to kill tumor cells. Types include external beam radiation, stereotactic radiosurgery (Gamma Knife), and proton therapy.\n\n**3. Chemotherapy**\nDrugs that kill rapidly dividing cells. Temozolomide is commonly used for gliomas. Can be oral or intravenous.\n\n**4. Targeted Therapy**\nDrugs targeting specific genetic mutations in tumor cells. Examples include Bevacizumab and Everolimus.\n\n**5. Immunotherapy**\nBoosts the immune system to recognize and attack cancer cells.\n\nTreatment is always personalized. A team of specialists creates the best plan for each patient.\n\nWould you like details about treatment for a specific tumor type?"

        # ===== PREVENTION =====
        if intent == 'prevention':
            return "**Brain Tumor Prevention & Risk Reduction:**\n\nWhile not all brain tumors can be prevented, you can reduce risk:\n\n**Lifestyle:**\n- Eat a diet rich in fruits, vegetables, and antioxidants\n- Exercise regularly (at least 30 minutes daily)\n- Maintain healthy weight\n- Get 7-8 hours of quality sleep\n\n**Avoid Risks:**\n- Minimize unnecessary radiation exposure\n- Avoid smoking and excessive alcohol\n- Limit exposure to industrial chemicals and pesticides\n- Use protective equipment in hazardous workplaces\n\n**Early Detection:**\n- Regular health checkups\n- Report persistent neurological symptoms promptly\n- Follow up on any abnormal findings\n- Know your family medical history\n\n**When to See a Doctor:**\n- Persistent headaches lasting more than 2 weeks\n- New seizures\n- Unexplained vision or hearing changes\n- Sudden personality or behavior changes"

        # ===== DOCTOR =====
        if intent == 'doctor':
            return "**Medical Specialists for Brain Tumors:**\n\n**1. Neurologist**\nFirst point of contact. Evaluates neurological symptoms, orders MRI scans, and provides initial diagnosis.\n\n**2. Neurosurgeon**\nPerforms brain surgery to remove or biopsy tumors. Specializes in minimally invasive techniques.\n\n**3. Neuro-oncologist**\nCancer specialist focused on brain tumors. Plans chemotherapy and targeted therapy.\n\n**4. Radiation Oncologist**\nDesigns and delivers radiation treatment plans.\n\n**5. Endocrinologist**\nFor pituitary tumors affecting hormone production.\n\n**6. Ophthalmologist**\nEvaluates vision problems caused by tumors pressing on optic nerves.\n\n**How to Get Started:**\nBegin with your primary care physician or a neurologist. Bring your NeuroTrack PDF report to your appointment for reference."

        # ===== MRI INFO =====
        if intent == 'mri_info':
            return "**About MRI Scans:**\n\n**What is MRI?**\nMagnetic Resonance Imaging uses powerful magnets and radio waves to create detailed images of the brain. Unlike CT scans, MRI does not use radiation.\n\n**Types of MRI Sequences:**\n- **T1-weighted:** Shows brain anatomy clearly\n- **T2-weighted:** Highlights fluid and swelling\n- **FLAIR:** Best for detecting abnormalities\n- **T1 with Contrast:** Uses gadolinium dye to highlight tumors\n- **DWI:** Shows cell density and tumor aggressiveness\n\n**What to Expect:**\n- Takes 30-60 minutes\n- You lie inside a tube-shaped machine\n- Loud knocking sounds are normal\n- You must stay very still\n- Contrast dye may be injected through IV\n\n**How NeuroTrack Uses MRI:**\nOur AI analyzes MRI images using a deep learning model trained on 5,600 real brain scans, achieving 92.77% accuracy in tumor classification."

        # ===== TUMOR GENERAL =====
        if intent == 'tumor_general':
            return "**About Brain Tumors:**\n\nA brain tumor is an abnormal growth of cells in the brain. Tumors can be benign (non-cancerous) or malignant (cancerous).\n\n**NeuroTrack detects 3 main types:**\n\n1. **Glioma** - Originates from glial cells. Can range from slow-growing to highly aggressive. Accounts for 80% of malignant brain tumors.\n\n2. **Meningioma** - Forms in the protective membranes around the brain. Usually benign and slow-growing. Most common primary brain tumor.\n\n3. **Pituitary Tumor** - Develops in the hormone-controlling pituitary gland. Usually benign and highly treatable.\n\n**General Symptoms:**\nHeadaches, seizures, vision changes, memory problems, personality changes, nausea, balance issues.\n\nWhich type would you like to learn more about?"

        # ===== PROGNOSIS =====
        if intent == 'prognosis':
            return "**Brain Tumor Prognosis by Type:**\n\n**Glioma:**\n- Grade 1-2: 5-10+ year survival possible\n- Grade 3: 2-5 year survival\n- Grade 4 (Glioblastoma): 12-18 months median\n- Early detection dramatically improves outcomes\n\n**Meningioma:**\n- 5-year survival rate: approximately 84%\n- Most are benign with excellent outcomes\n- Many patients live completely normal lives\n- Regular monitoring recommended\n\n**Pituitary Tumor:**\n- 5-year survival rate: over 97%\n- Excellent prognosis in most cases\n- Hormone function usually restored with treatment\n- Minimally invasive surgery available\n\n**Important Factors:**\n- Tumor type and grade\n- Size and location\n- Patient age and overall health\n- Response to treatment\n- Genetic markers\n\nAlways discuss specific prognosis with your medical team. Statistics are averages, not individual predictions."

        # ===== UNKNOWN / DEFAULT =====
        responses = [
            f"I want to make sure I give you the best answer. I am specialized in brain tumor information and the NeuroTrack system. Could you rephrase your question? For example, you can ask about:\n\n- Brain tumor types\n- Symptoms or treatments\n- How to upload an MRI\n- Understanding your results\n- When to see a doctor",
            f"That is an interesting question! As your NeuroTrack assistant, I am best at helping with brain health topics. Try asking me about:\n\n- Glioma, Meningioma, or Pituitary tumors\n- MRI scan information\n- Your scan results\n- Treatment options\n- Prevention tips",
            f"I am not sure I understood that correctly. I am your NeuroTrack AI guide, focused on brain tumor detection and awareness. Here are some things I can help with:\n\n- Upload MRI guide\n- Dashboard explanation\n- Tumor information\n- Symptoms and treatments\n- Doctor recommendations\n\nWhat would you like to know?"
        ]
        return self.get_varied_response('default', responses)


chatbot = NeuroTrackChatbot()