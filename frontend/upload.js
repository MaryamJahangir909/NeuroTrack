document.addEventListener('DOMContentLoaded', function() {
    loadPatients();
});

async function loadPatients() {
    try {
        const response = await fetch(API_URL + '/api/patients');
        const data = await response.json();

        const select = document.getElementById('patient-select');
        select.innerHTML = '<option value="">-- Select Patient --</option>';

        if (data.success && data.patients.length > 0) {
            data.patients.forEach(function(patient) {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = patient.name + ' (Age: ' + patient.age + ')';
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

function addPatient() {
    var name = document.getElementById('patient-name').value.trim();
    var age = document.getElementById('patient-age').value.trim();
    var email = document.getElementById('patient-email').value.trim();
    var phone = document.getElementById('patient-phone').value.trim();

    // Validate Name
    if (!name) {
        alert('Please enter patient name!');
        return;
    }

    if (name.length < 2) {
        alert('Name must be at least 2 characters!');
        return;
    }

    var nameRegex = /^[a-zA-Z\s]+$/;
    if (!nameRegex.test(name)) {
        alert('Name must contain only letters and spaces. Numbers are not allowed!');
        document.getElementById('patient-name').value = '';
        return;
    }

    // Validate Age
    if (!age) {
        alert('Please enter patient age!');
        return;
    }

    var ageNum = parseInt(age);
    if (isNaN(ageNum)) {
        alert('Age must be a valid number!');
        return;
    }

    if (ageNum < 1) {
        alert('Age cannot be negative or zero! Please enter a valid age.');
        document.getElementById('patient-age').value = '';
        return;
    }

    if (ageNum > 120) {
        alert('Please enter a valid age between 1 and 120!');
        document.getElementById('patient-age').value = '';
        return;
    }

    // Validate Email
    if (!email) {
        alert('Please enter email address!');
        return;
    }

    var emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address!\nExample: john@gmail.com');
        document.getElementById('patient-email').value = '';
        return;
    }

    // Validate Phone (optional)
    if (phone) {
        var cleanPhone = phone.replace(/[\+\-\s]/g, '');
        if (!/^\d+$/.test(cleanPhone)) {
            alert('Phone number must contain only digits!');
            document.getElementById('patient-phone').value = '';
            return;
        }
        if (cleanPhone.length < 10 || cleanPhone.length > 15) {
            alert('Phone number must be 10-15 digits!');
            document.getElementById('patient-phone').value = '';
            return;
        }
    }

    // All validation passed - send to backend
    fetch(API_URL + '/api/patients', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            age: ageNum,
            email: email,
            phone: phone
        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            alert('Patient ' + name + ' added successfully!');
            document.getElementById('patient-name').value = '';
            document.getElementById('patient-age').value = '';
            document.getElementById('patient-email').value = '';
            document.getElementById('patient-phone').value = '';
            loadPatients();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(function(error) {
        alert('Error connecting to server');
    });
}

function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            const placeholder = document.getElementById('upload-placeholder');
            preview.src = e.target.result;
            preview.style.display = 'block';
            placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

function analyzeMRI() {
    const patientId = document.getElementById('patient-select').value;
    const fileInput = document.getElementById('mri-file');
    const file = fileInput.files[0];

    if (!patientId) {
        alert('Please select a patient first');
        return;
    }

    if (!file) {
        alert('Please upload an MRI image');
        return;
    }

    const btn = document.getElementById('analyze-btn');
    btn.textContent = 'Analyzing...';
    btn.disabled = true;

    document.getElementById('result-section').style.display = 'none';
    document.getElementById('heatmap-section').style.display = 'none';
    document.getElementById('download-report-btn').style.display = 'none';

    const formData = new FormData();
    formData.append('mri_image', file);
    formData.append('patient_id', patientId);

    fetch(API_URL + '/api/predict', {
        method: 'POST',
        body: formData
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            showResult(data);
        } else {
            document.getElementById('result-section').style.display = 'block';
            document.getElementById('result-tumor-type').textContent = 'INVALID IMAGE';
            document.getElementById('result-confidence').textContent = data.error;
            var header = document.getElementById('result-header');
            header.style.background = 'rgba(255, 165, 0, 0.2)';
            header.style.borderLeft = '5px solid orange';
        }
        btn.textContent = 'Analyze MRI';
        btn.disabled = false;
    })
    .catch(function(error) {
        alert('Error connecting to server');
        btn.textContent = 'Analyze MRI';
        btn.disabled = false;
    });
}

function showResult(data) {
    var prediction = data.prediction;

    document.getElementById('result-section').style.display = 'block';
    document.getElementById('result-tumor-type').textContent =
        prediction.tumor_type.toUpperCase();
    document.getElementById('result-confidence').textContent =
        'Confidence: ' + prediction.confidence + '%';

    var header = document.getElementById('result-header');
    if (prediction.is_tumor) {
        header.style.background = 'rgba(255, 50, 50, 0.2)';
        header.style.borderLeft = '5px solid #ff3232';
    } else {
        header.style.background = 'rgba(0, 255, 136, 0.2)';
        header.style.borderLeft = '5px solid #00ff88';
    }

    var probs = prediction.probabilities;
    setBar('glioma', probs.glioma);
    setBar('meningioma', probs.meningioma);
    setBar('notumor', probs.notumor);
    setBar('pituitary', probs.pituitary);

    // Show heatmap
    if (data.heatmap) {
        var heatmapSection = document.getElementById('heatmap-section');
        var heatmapImg = document.getElementById('heatmap-image');
        heatmapImg.src = data.heatmap;
        heatmapSection.style.display = 'block';
    }
        // Show 3D Brain Model
    var brain3dSection = document.getElementById('brain3d-section');
    if (brain3dSection) {
        brain3dSection.style.display = 'block';
        Brain3D.init('brain3d-container', prediction.tumor_type);
    }
        // Show MRI Viewer
    var viewerSection = document.getElementById('mri-viewer-section');
    if (viewerSection) {
        var previewImg = document.getElementById('image-preview');
        if (previewImg && previewImg.src) {
            viewerSection.style.display = 'block';
            MRIViewer.init(previewImg.src);
        }
    }

    // Show download report button
    var reportBtn = document.getElementById('download-report-btn');
    reportBtn.style.display = 'block';
    reportBtn.onclick = function() {
        downloadReport(data.scan_id);
    };

    document.getElementById('result-section').scrollIntoView({
        behavior: 'smooth'
    });
}

function downloadReport(scanId) {
    var btn = document.getElementById('download-report-btn');
    btn.textContent = 'Generating Report...';
    btn.disabled = true;

    window.open(API_URL + '/api/report/' + scanId, '_blank');

    setTimeout(function() {
        btn.textContent = 'Download PDF Report';
        btn.disabled = false;
    }, 2000);
}

function setBar(name, value) {
    document.getElementById('bar-' + name).style.width = value + '%';
    document.getElementById('val-' + name).textContent = value + '%';
}