const API_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    updateNavbar();
    loadTheme();
});

function updateNavbar() {
    const name = localStorage.getItem('name');
    const role = localStorage.getItem('role');
    const navLinks = document.querySelector('.nav-links');

    if (name && navLinks) {
        navLinks.innerHTML =
            '<a href="index.html">Home</a>' +
            '<a href="upload.html">Upload MRI</a>' +
            '<a href="dashboard.html">Dashboard</a>' +
            '<a href="analytics.html">Analytics</a>' +
            '<a href="chatbot.html">AI Assistant</a>' +
            '<div class="nav-user">' +
            '<span class="nav-user-name">' + name + '</span>' +
            '<span class="nav-user-role">' + role.toUpperCase() + '</span>' +
            '<button class="theme-btn" onclick="toggleTheme()">Theme</button>' +
            '<button class="logout-btn" onclick="logout()">Logout</button>' +
            '</div>';
    }
}

function toggleTheme() {
    var body = document.body;
    var currentTheme = localStorage.getItem('theme') || 'dark';

    var themes = ['dark', 'light', 'pink', 'blue'];
    var currentIndex = themes.indexOf(currentTheme);
    var nextIndex = (currentIndex + 1) % themes.length;
    var nextTheme = themes[nextIndex];

    body.classList.remove('theme-light', 'theme-pink', 'theme-blue');

    if (nextTheme !== 'dark') {
        body.classList.add('theme-' + nextTheme);
    }

    localStorage.setItem('theme', nextTheme);

    // Show theme name briefly
    showThemeNotification(nextTheme);
}

function showThemeNotification(themeName) {
    var existing = document.getElementById('theme-notif');
    if (existing) existing.remove();

    var notif = document.createElement('div');
    notif.id = 'theme-notif';
    notif.style.cssText =
        'position:fixed; top:80px; right:30px; ' +
        'background:var(--gradient-primary); color:white; ' +
        'padding:12px 24px; border-radius:12px; ' +
        'font-weight:700; font-size:14px; z-index:9999; ' +
        'box-shadow:0 4px 20px rgba(0,0,0,0.3); ' +
        'animation:slideIn 0.3s ease;';
    notif.textContent = 'Theme: ' + themeName.toUpperCase();
    document.body.appendChild(notif);

    setTimeout(function() {
        notif.style.opacity = '0';
        setTimeout(function() { notif.remove(); }, 300);
    }, 1500);
}

function loadTheme() {
    var theme = localStorage.getItem('theme') || 'dark';
    if (theme !== 'dark') {
        document.body.classList.add('theme-' + theme);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
    localStorage.removeItem('name');
    window.location.href = 'login.html';
}

async function loadStats() {
    try {
        const response = await fetch(API_URL + '/api/dashboard');
        const data = await response.json();

        if (data.success) {
            const totalScans = document.getElementById('total-scans');
            const totalPatients = document.getElementById('total-patients');
            const tumorDetected = document.getElementById('tumor-detected');
            const noTumor = document.getElementById('no-tumor');

            if (totalScans) totalScans.textContent = data.stats.total_scans;
            if (totalPatients) totalPatients.textContent = data.stats.total_patients;
            if (tumorDetected) tumorDetected.textContent = data.stats.tumor_detected;
            if (noTumor) noTumor.textContent = data.stats.no_tumor;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function checkAuth() {
    var token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

function checkDoctorAuth() {
    var token = localStorage.getItem('token');
    var role = localStorage.getItem('role');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    if (role !== 'doctor') {
        window.location.href = 'upload.html';
        return false;
    }
    return true;
}