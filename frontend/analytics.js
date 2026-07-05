document.addEventListener('DOMContentLoaded', function() {
    loadAnalytics();
});

function loadAnalytics() {
    fetch(API_URL + '/api/dashboard')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            updateSummaryCards(data.stats);
            buildTumorPieChart(data.stats);
            buildDetectionDoughnut(data.stats);
            buildCategoryBar(data.stats);
            buildConfidenceBar(data.stats);
            buildPerformanceRadar(data.stats);
            buildRiskPolar(data.stats);
            loadScanHistory(data.recent_scans);
        }
    })
    .catch(function(error) {
        console.error('Analytics error:', error);
    });
}

function updateSummaryCards(stats) {
    document.getElementById('total-scans').textContent =
        stats.total_scans;
    document.getElementById('total-patients').textContent =
        stats.total_patients;
    document.getElementById('tumor-detected').textContent =
        stats.tumor_detected;

    var rate = stats.total_scans > 0
        ? Math.round((stats.tumor_detected / stats.total_scans) * 100)
        : 0;
    document.getElementById('detection-rate').textContent = rate + '%';
}

function buildTumorPieChart(stats) {
    var ctx = document.getElementById('tumorPieChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
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
                    'rgba(255, 99, 132, 0.85)',
                    'rgba(255, 159, 64, 0.85)',
                    'rgba(153, 102, 255, 0.85)',
                    'rgba(0, 217, 255, 0.85)'
                ],
                borderColor: '#1a1a2e',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            var total = context.dataset.data.reduce(
                                function(a, b) { return a + b; }, 0
                            );
                            var percentage = total > 0
                                ? Math.round((context.raw / total) * 100)
                                : 0;
                            return context.label + ': ' +
                                context.raw + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

function buildDetectionDoughnut(stats) {
    var ctx = document.getElementById('detectionDoughnut').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Tumor Detected', 'No Tumor'],
            datasets: [{
                data: [
                    stats.tumor_detected || 0,
                    stats.no_tumor || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.85)',
                    'rgba(0, 255, 136, 0.85)'
                ],
                borderColor: '#1a1a2e',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 15,
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function buildCategoryBar(stats) {
    var ctx = document.getElementById('categoryBar').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
            datasets: [{
                label: 'Number of Scans',
                data: [
                    stats.glioma || 0,
                    stats.meningioma || 0,
                    stats.pituitary || 0,
                    stats.no_tumor || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(0, 217, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(0, 217, 255, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#aaaaaa',
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    }
                },
                x: {
                    ticks: { color: '#aaaaaa' },
                    grid: { display: false }
                }
            }
        }
    });
}

function buildConfidenceBar(stats) {
    var ctx = document.getElementById('confidenceBar').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
            datasets: [{
                label: 'Avg Confidence %',
                data: [92, 88, 95, 99],
                backgroundColor: 'rgba(0, 217, 255, 0.2)',
                borderColor: 'rgba(0, 217, 255, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#aaaaaa',
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    }
                },
                y: {
                    ticks: { color: '#aaaaaa' },
                    grid: { display: false }
                }
            }
        }
    });
}

function buildPerformanceRadar(stats) {
    var ctx = document.getElementById('performanceRadar').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Accuracy',
                'Precision',
                'Recall',
                'F1 Score',
                'Confidence',
                'Speed'
            ],
            datasets: [{
                label: 'AI Model Performance',
                data: [92.77, 91, 90, 91, 94, 88],
                backgroundColor: 'rgba(0, 217, 255, 0.15)',
                borderColor: 'rgba(0, 217, 255, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(0, 217, 255, 1)',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: { size: 12 }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#aaaaaa',
                        backdropColor: 'transparent',
                        stepSize: 20
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#cccccc',
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

function buildRiskPolar(stats) {
    var ctx = document.getElementById('riskPolar').getContext('2d');
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Glioma Risk', 'Meningioma Risk', 'Pituitary Risk', 'Clear'],
            datasets: [{
                data: [
                    stats.glioma || 0,
                    stats.meningioma || 0,
                    stats.pituitary || 0,
                    stats.no_tumor || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(0, 255, 136, 0.7)'
                ],
                borderColor: '#1a1a2e',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 12,
                        font: { size: 11 }
                    }
                }
            },
            scales: {
                r: {
                    ticks: {
                        color: '#aaaaaa',
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

function loadScanHistory(scans) {
    var tbody = document.getElementById('history-tbody');
    tbody.innerHTML = '';

    if (!scans || scans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10">No scans found</td></tr>';
        return;
    }

    scans.forEach(function(scan) {
        var isTumor = scan.predicted_class !== 'notumor';
        var statusClass = isTumor ? 'status-danger' : 'status-safe';
        var statusText = isTumor ? 'Tumor Detected' : 'Clear';

        var row = document.createElement('tr');
        row.innerHTML =
            '<td>' + scan.id + '</td>' +
            '<td>' + scan.patient_name + '</td>' +
            '<td><strong>' + scan.predicted_class.toUpperCase() + '</strong></td>' +
            '<td>' + scan.confidence_score + '%</td>' +
            '<td>' + scan.probabilities.glioma + '%</td>' +
            '<td>' + scan.probabilities.meningioma + '%</td>' +
            '<td>' + scan.probabilities.pituitary + '%</td>' +
            '<td>' + scan.probabilities.notumor + '%</td>' +
            '<td>' + scan.scan_date + '</td>' +
            '<td class="' + statusClass + '">' + statusText + '</td>';
        tbody.appendChild(row);
    });
}