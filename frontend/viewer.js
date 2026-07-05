var MRIViewer = {
    currentImage: null,
    zoom: 1,
    brightness: 100,
    contrast: 100,
    isDragging: false,
    lastX: 0,
    lastY: 0,
    offsetX: 0,
    offsetY: 0,

    init: function(imageSource) {
        this.currentImage = imageSource;
        this.zoom = 1;
        this.brightness = 100;
        this.contrast = 100;
        this.offsetX = 0;
        this.offsetY = 0;
        this.render();
        this.addMouseControls();
    },

    addMouseControls: function() {
        var views = ['axial', 'sagittal', 'coronal'];
        var self = this;

        views.forEach(function(view) {
            var canvas = document.getElementById('canvas-' + view);
            if (!canvas) return;

            // Mouse wheel zoom
            canvas.addEventListener('wheel', function(e) {
                e.preventDefault();
                if (e.deltaY < 0) {
                    self.zoom = Math.min(self.zoom + 0.1, 4);
                } else {
                    self.zoom = Math.max(self.zoom - 0.1, 0.3);
                }
                self.render();
            });

            // Mouse drag to pan
            canvas.addEventListener('mousedown', function(e) {
                self.isDragging = true;
                self.lastX = e.offsetX;
                self.lastY = e.offsetY;
                canvas.style.cursor = 'grabbing';
            });

            canvas.addEventListener('mousemove', function(e) {
                if (self.isDragging) {
                    var dx = e.offsetX - self.lastX;
                    var dy = e.offsetY - self.lastY;
                    self.offsetX += dx;
                    self.offsetY += dy;
                    self.lastX = e.offsetX;
                    self.lastY = e.offsetY;
                    self.render();
                }

                // Show coordinates
                var coordsEl = document.getElementById('mouse-coords');
                if (coordsEl) {
                    coordsEl.textContent = 'X: ' + e.offsetX + ' Y: ' + e.offsetY;
                }
            });

            canvas.addEventListener('mouseup', function() {
                self.isDragging = false;
                canvas.style.cursor = 'crosshair';
            });

            canvas.addEventListener('mouseleave', function() {
                self.isDragging = false;
                canvas.style.cursor = 'crosshair';
            });

            // Touch controls for mobile
            canvas.addEventListener('touchstart', function(e) {
                e.preventDefault();
                var touch = e.touches[0];
                var rect = canvas.getBoundingClientRect();
                self.isDragging = true;
                self.lastX = touch.clientX - rect.left;
                self.lastY = touch.clientY - rect.top;
            });

            canvas.addEventListener('touchmove', function(e) {
                e.preventDefault();
                if (self.isDragging) {
                    var touch = e.touches[0];
                    var rect = canvas.getBoundingClientRect();
                    var currentX = touch.clientX - rect.left;
                    var currentY = touch.clientY - rect.top;
                    self.offsetX += currentX - self.lastX;
                    self.offsetY += currentY - self.lastY;
                    self.lastX = currentX;
                    self.lastY = currentY;
                    self.render();
                }
            });

            canvas.addEventListener('touchend', function() {
                self.isDragging = false;
            });
        });
    },

    render: function() {
        var self = this;
        var views = ['axial', 'sagittal', 'coronal'];
        var viewLabels = ['AXIAL', 'SAGITTAL', 'CORONAL'];
        var viewColors = ['#00d9ff', '#00ff88', '#ff6b6b'];

        var filters = [
            'brightness(' + this.brightness + '%) contrast(' + this.contrast + '%)',
            'brightness(' + (this.brightness - 10) + '%) contrast(' + (this.contrast + 10) + '%)',
            'brightness(' + (this.brightness + 10) + '%) contrast(' + (this.contrast - 10) + '%)'
        ];

        views.forEach(function(view, index) {
            var canvas = document.getElementById('canvas-' + view);
            if (!canvas) return;

            var ctx = canvas.getContext('2d');
            var img = new window.Image();

            img.onload = function() {
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Fill black background
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Apply filter
                ctx.filter = filters[index];
                ctx.save();

                // Apply zoom and pan
                ctx.translate(
                    canvas.width / 2 + self.offsetX,
                    canvas.height / 2 + self.offsetY
                );
                ctx.scale(self.zoom, self.zoom);

                // Apply view transformation
                if (index === 1) {
                    ctx.scale(-1, 1);
                } else if (index === 2) {
                    ctx.rotate(90 * Math.PI / 180);
                }

                // Draw image centered
                ctx.drawImage(
                    img,
                    -canvas.width / 2,
                    -canvas.height / 2,
                    canvas.width,
                    canvas.height
                );
                ctx.restore();
                ctx.filter = 'none';

                // Draw view label
                ctx.fillStyle = viewColors[index];
                ctx.font = 'bold 12px Arial';
                ctx.fillText(viewLabels[index], 8, 18);

                // Draw crosshair
                ctx.strokeStyle = 'rgba(0, 217, 255, 0.3)';
                ctx.lineWidth = 1;
                ctx.setLineDash([4, 4]);

                ctx.beginPath();
                ctx.moveTo(canvas.width / 2, 0);
                ctx.lineTo(canvas.width / 2, canvas.height);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);
                ctx.lineTo(canvas.width, canvas.height / 2);
                ctx.stroke();

                ctx.setLineDash([]);

                // Draw border info
                ctx.fillStyle = 'rgba(255,255,255,0.4)';
                ctx.font = '10px Arial';
                ctx.fillText('Zoom: ' + self.zoom.toFixed(1) + 'x', 8, canvas.height - 8);

                // Draw orientation markers
                ctx.fillStyle = viewColors[index];
                ctx.font = 'bold 10px Arial';
                if (index === 0) {
                    ctx.fillText('A', canvas.width / 2 - 4, 30);
                    ctx.fillText('P', canvas.width / 2 - 4, canvas.height - 12);
                    ctx.fillText('R', 8, canvas.height / 2 + 4);
                    ctx.fillText('L', canvas.width - 14, canvas.height / 2 + 4);
                } else if (index === 1) {
                    ctx.fillText('A', 8, canvas.height / 2 + 4);
                    ctx.fillText('P', canvas.width - 14, canvas.height / 2 + 4);
                    ctx.fillText('S', canvas.width / 2 - 4, 30);
                    ctx.fillText('I', canvas.width / 2 - 4, canvas.height - 12);
                } else {
                    ctx.fillText('S', canvas.width / 2 - 4, 30);
                    ctx.fillText('I', canvas.width / 2 - 4, canvas.height - 12);
                    ctx.fillText('R', 8, canvas.height / 2 + 4);
                    ctx.fillText('L', canvas.width - 14, canvas.height / 2 + 4);
                }
            };

            img.src = self.currentImage;
        });
    },

    zoomIn: function() {
        if (this.zoom < 4) {
            this.zoom += 0.2;
            this.render();
        }
    },

    zoomOut: function() {
        if (this.zoom > 0.3) {
            this.zoom -= 0.2;
            this.render();
        }
    },

    resetZoom: function() {
        this.zoom = 1;
        this.brightness = 100;
        this.contrast = 100;
        this.offsetX = 0;
        this.offsetY = 0;
        document.getElementById('brightness-val').textContent = '100%';
        document.getElementById('contrast-val').textContent = '100%';
        var brightSlider = document.querySelector('input[oninput*="Brightness"]');
        var contrastSlider = document.querySelector('input[oninput*="Contrast"]');
        if (brightSlider) brightSlider.value = 100;
        if (contrastSlider) contrastSlider.value = 100;
        this.render();
    },

    updateBrightness: function(value) {
        this.brightness = parseInt(value);
        document.getElementById('brightness-val').textContent = value + '%';
        this.render();
    },

    updateContrast: function(value) {
        this.contrast = parseInt(value);
        document.getElementById('contrast-val').textContent = value + '%';
        this.render();
    },

    invertColors: function() {
        var views = ['axial', 'sagittal', 'coronal'];
        views.forEach(function(view) {
            var canvas = document.getElementById('canvas-' + view);
            if (!canvas) return;
            var ctx = canvas.getContext('2d');
            var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            var data = imageData.data;
            for (var i = 0; i < data.length; i += 4) {
                data[i] = 255 - data[i];
                data[i + 1] = 255 - data[i + 1];
                data[i + 2] = 255 - data[i + 2];
            }
            ctx.putImageData(imageData, 0, 0);
        });
    }
};