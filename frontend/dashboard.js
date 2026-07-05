window.deletePatient = function(patientId) {
    var confirmed = confirm('Delete this patient and all their scan history?');
    if (!confirmed) return;

    fetch(API_URL + '/api/patients/' + patientId, {
        method: 'DELETE'
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            alert('Patient deleted successfully!');
            loadDashboard();
            loadAllPatients();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(function() {
        alert('Error connecting to server');
    });
};

document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadAllPatients();
});

function loadDashboard() {
    fetch(API_URL + '/api/dashboard')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            var totalScans = document.getElementById('total-scans');
            var totalPatients = document.getElementById('total-patients');
            var tumorDetected = document.getElementById('tumor-detected');
            var noTumor = document.getElementById('no-tumor');

            if (totalScans) totalScans.textContent = data.stats.total_scans;
            if (totalPatients) totalPatients.textContent = data.stats.total_patients;
            if (tumorDetected) tumorDetected.textContent = data.stats.tumor_detected;
            if (noTumor) noTumor.textContent = data.stats.no_tumor;

            buildTumorChart(data.stats);
            buildOverviewChart(data.stats);

            var tbody = document.getElementById('scans-tbody');
            if (!tbody) return;
            tbody.innerHTML = '';

            if (data.recent_scans.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No scans yet</td></tr>';
                return;
            }

            data.recent_scans.forEach(function(scan) {
                var isTumor = scan.predicted_class !== 'notumor';
                var statusClass = isTumor ? 'status-danger' : 'status-safe';
                var statusText = isTumor ? 'Tumor Detected' : 'Clear';

                var row = document.createElement('tr');
                row.innerHTML =
                    '<td>' + scan.id + '</td>' +
                    '<td>' + scan.patient_name + '</td>' +
                    '<td>' + scan.predicted_class.toUpperCase() + '</td>' +
                    '<td>' + scan.confidence_score + '%</td>' +
                    '<td>' + scan.scan_date + '</td>' +
                    '<td class="' + statusClass + '">' + statusText + '</td>';
                tbody.appendChild(row);
            });
        }
    })
    .catch(function(error) {
        console.error('Dashboard error:', error);
    });
}

function buildTumorChart(stats) {
    var canvas = document.getElementById('tumorChart');
    if (!canvas) return;
    new Chart(canvas.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
            datasets: [{
                data: [
                    stats.glioma || 0,
                    stats.meningioma || 0,
                    stats.pituitary || 0,
                    stats.no_tumor || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(0, 217, 255, 0.8)'
                ],
                borderColor: '#1a1a2e',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 15,
                        font: { size: 13 }
                    }
                }
            }
        }
    });
}

function buildOverviewChart(stats) {
    var canvas = document.getElementById('overviewChart');
    if (!canvas) return;
    new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Total Scans', 'Tumor Detected', 'No Tumor', 'Patients'],
            datasets: [{
                label: 'Count',
                data: [
                    stats.total_scans,
                    stats.tumor_detected,
                    stats.no_tumor,
                    stats.total_patients
                ],
                backgroundColor: [
                    'rgba(0, 217, 255, 0.7)',
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(0, 255, 136, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(0, 217, 255, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(0, 255, 136, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#aaaaaa', stepSize: 1 },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: '#aaaaaa' },
                    grid: { display: false }
                }
            }
        }
    });
}

function loadAllPatients() {
    fetch(API_URL + '/api/patients')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        var container = document.getElementById('patients-list');
        if (!container) return;
        container.innerHTML = '';

        if (!data.success || data.patients.length === 0) {
            container.innerHTML = '<p>No patients registered yet</p>';
            return;
        }

        data.patients.forEach(function(patient) {
            var card = document.createElement('div');
            card.className = 'patient-card';

            var deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.style.cssText =
                'background:rgba(255,68,68,0.1);' +
                'border:1px solid rgba(255,68,68,0.3);' +
                'color:#ff4444;' +
                'padding:8px 16px;' +
                'border-radius:8px;' +
                'cursor:pointer;' +
                'font-size:13px;' +
                'font-weight:bold;';

            deleteBtn.addEventListener('click', function() {
                window.deletePatient(patient.id);
            });

            var info = document.createElement('div');
            info.innerHTML =
                '<h3>' + patient.name + '</h3>' +
                '<p>Age: ' + patient.age + '</p>' +
                '<p>Email: ' + patient.email + '</p>' +
                '<p>Registered: ' + patient.created_at + '</p>';

            card.style.display = 'flex';
            card.style.justifyContent = 'space-between';
            card.style.alignItems = 'center';

            card.appendChild(info);
            card.appendChild(deleteBtn);
            container.appendChild(card);
        });
    })
    .catch(function(error) {
        console.error('Patients error:', error);
    });
}