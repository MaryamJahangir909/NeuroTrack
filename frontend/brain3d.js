var Brain3D = {
    init: function(containerId, tumorType) {
        var container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';

        var width = container.clientWidth || 500;
        var height = 400;

        // Tumor info per type
        var tumorData = {
            'glioma': {
                color: '#ff3333',
                glowColor: 'rgba(255, 51, 51, 0.6)',
                position: { top: '30%', left: '60%' },
                size: 50,
                name: 'GLIOMA',
                description: 'Tumor in cerebral hemisphere'
            },
            'meningioma': {
                color: '#ff8800',
                glowColor: 'rgba(255, 136, 0, 0.6)',
                position: { top: '20%', left: '70%' },
                size: 45,
                name: 'MENINGIOMA',
                description: 'Tumor in meninges (outer brain layer)'
            },
            'pituitary': {
                color: '#9932cc',
                glowColor: 'rgba(153, 50, 204, 0.6)',
                position: { top: '55%', left: '45%' },
                size: 35,
                name: 'PITUITARY TUMOR',
                description: 'Tumor in pituitary gland'
            },
            'notumor': {
                color: '#00ff88',
                glowColor: 'rgba(0, 255, 136, 0.4)',
                name: 'HEALTHY BRAIN',
                description: 'No tumor detected'
            }
        };

        var tumor = tumorData[tumorType] || tumorData['notumor'];

        // Create the visualization
        var html = `
            <div style="position:relative; width:100%; height:${height}px; 
                        background:radial-gradient(ellipse at center, #1a1a3a 0%, #0a0e1a 100%);
                        border-radius:15px; overflow:hidden; display:flex;
                        align-items:center; justify-content:center;">

                <!-- Header -->
                <div style="position:absolute; top:15px; left:20px; z-index:10;">
                    <div style="color:#00d9ff; font-size:14px; font-weight:bold;
                                letter-spacing:1px;">3D BRAIN ANALYSIS</div>
                    <div style="color:${tumor.color}; font-size:12px;
                                font-weight:bold; margin-top:3px;">
                        ${tumor.name}
                    </div>
                </div>

                <!-- Stats -->
                <div style="position:absolute; top:15px; right:20px; z-index:10;
                            text-align:right;">
                    <div style="color:#00d9ff; font-size:11px;">STATUS</div>
                    <div style="color:${tumorType === 'notumor' ? '#00ff88' : '#ff4444'};
                                font-size:13px; font-weight:bold;">
                        ${tumorType === 'notumor' ? 'NORMAL' : 'ATTENTION REQUIRED'}
                    </div>
                </div>

                <!-- Brain Container -->
                <div id="brain-wrapper" style="position:relative; width:300px;
                                                height:300px; perspective:1000px;
                                                transform-style:preserve-3d;">

                    <!-- Brain SVG -->
                    <svg id="brain-svg" viewBox="0 0 200 220" 
                         style="width:100%; height:100%;
                                filter:drop-shadow(0 0 30px rgba(0,217,255,0.4));
                                transition:transform 0.1s;">

                        <!-- Brain outer shadow -->
                        <ellipse cx="100" cy="115" rx="85" ry="95"
                                 fill="rgba(100,150,255,0.05)"/>

                        <!-- Brain body (transparent blue) -->
                        <path d="M100,25 
                                 C140,25 175,55 175,105
                                 C175,145 170,180 155,200
                                 C145,210 125,215 100,215
                                 C75,215 55,210 45,200
                                 C30,180 25,145 25,105
                                 C25,55 60,25 100,25 Z"
                              fill="url(#brainGradient)"
                              stroke="rgba(100,200,255,0.6)"
                              stroke-width="1.5"/>

                        <!-- Brain folds (sulci) -->
                        <g stroke="rgba(100,180,255,0.4)" stroke-width="1" fill="none">
                            <!-- Left hemisphere folds -->
                            <path d="M50,60 Q60,65 55,75 Q50,85 60,90"/>
                            <path d="M45,90 Q55,95 50,105 Q45,115 55,120"/>
                            <path d="M50,125 Q60,130 55,140 Q50,150 60,155"/>
                            <path d="M55,160 Q65,165 60,175 Q55,185 65,190"/>

                            <!-- Right hemisphere folds -->
                            <path d="M150,60 Q140,65 145,75 Q150,85 140,90"/>
                            <path d="M155,90 Q145,95 150,105 Q155,115 145,120"/>
                            <path d="M150,125 Q140,130 145,140 Q150,150 140,155"/>
                            <path d="M145,160 Q135,165 140,175 Q145,185 135,190"/>

                            <!-- Top folds -->
                            <path d="M80,40 Q90,50 85,60"/>
                            <path d="M120,40 Q110,50 115,60"/>
                            <path d="M70,55 Q85,65 75,75"/>
                            <path d="M130,55 Q115,65 125,75"/>
                        </g>

                        <!-- Center fissure -->
                        <path d="M100,30 Q98,80 100,130 Q102,180 100,210"
                              stroke="rgba(80,150,220,0.5)" stroke-width="1.5"
                              fill="none"/>

                        <!-- Cerebellum hint at bottom -->
                        <ellipse cx="100" cy="195" rx="40" ry="15"
                                 fill="rgba(100,180,255,0.15)"
                                 stroke="rgba(100,180,255,0.3)"
                                 stroke-width="1"/>

                        <!-- Definitions -->
                        <defs>
                            <radialGradient id="brainGradient" cx="50%" cy="40%">
                                <stop offset="0%" stop-color="rgba(150,200,255,0.3)"/>
                                <stop offset="50%" stop-color="rgba(80,150,220,0.2)"/>
                                <stop offset="100%" stop-color="rgba(40,80,160,0.15)"/>
                            </radialGradient>

                            <radialGradient id="tumorGradient">
                                <stop offset="0%" stop-color="#ffffff"/>
                                <stop offset="40%" stop-color="${tumor.color}"/>
                                <stop offset="100%" stop-color="${tumor.color}aa"/>
                            </radialGradient>

                            <filter id="glow">
                                <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                                <feMerge>
                                    <feMergeNode in="coloredBlur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                        </defs>

                        ${tumorType !== 'notumor' ? `
                            <!-- Tumor highlighted area -->
                            <circle id="tumor-glow"
                                    cx="${tumor.position.left === '60%' ? 130 : tumor.position.left === '70%' ? 145 : 100}"
                                    cy="${tumor.position.top === '30%' ? 75 : tumor.position.top === '20%' ? 55 : 130}"
                                    r="35"
                                    fill="${tumor.color}"
                                    opacity="0.3"
                                    filter="url(#glow)">
                                <animate attributeName="r" 
                                         values="30;40;30" 
                                         dur="2s" 
                                         repeatCount="indefinite"/>
                                <animate attributeName="opacity" 
                                         values="0.3;0.5;0.3" 
                                         dur="2s" 
                                         repeatCount="indefinite"/>
                            </circle>

                            <!-- Tumor body -->
                            <circle id="tumor-body"
                                    cx="${tumor.position.left === '60%' ? 130 : tumor.position.left === '70%' ? 145 : 100}"
                                    cy="${tumor.position.top === '30%' ? 75 : tumor.position.top === '20%' ? 55 : 130}"
                                    r="15"
                                    fill="url(#tumorGradient)"
                                    stroke="${tumor.color}"
                                    stroke-width="2">
                                <animate attributeName="r" 
                                         values="13;17;13" 
                                         dur="1.5s" 
                                         repeatCount="indefinite"/>
                            </circle>

                            <!-- Pointer line -->
                            <line x1="${tumor.position.left === '60%' ? 145 : tumor.position.left === '70%' ? 160 : 115}"
                                  y1="${tumor.position.top === '30%' ? 75 : tumor.position.top === '20%' ? 55 : 130}"
                                  x2="${tumor.position.left === '60%' ? 195 : tumor.position.left === '70%' ? 200 : 175}"
                                  y2="${tumor.position.top === '30%' ? 50 : tumor.position.top === '20%' ? 30 : 110}"
                                  stroke="${tumor.color}" stroke-width="1.5"/>

                            <circle cx="${tumor.position.left === '60%' ? 195 : tumor.position.left === '70%' ? 200 : 175}"
                                    cy="${tumor.position.top === '30%' ? 50 : tumor.position.top === '20%' ? 30 : 110}"
                                    r="3" fill="${tumor.color}"/>
                        ` : ''}
                    </svg>
                </div>

                <!-- Info Panel -->
                <div style="position:absolute; bottom:15px; left:20px; right:20px;
                            display:flex; justify-content:space-between;
                            align-items:flex-end; z-index:10;">

                    <div style="background:rgba(0,0,0,0.5); padding:8px 12px;
                                border-radius:8px; border-left:3px solid ${tumor.color};
                                max-width:60%;">
                        <div style="color:${tumor.color}; font-size:11px;
                                    font-weight:bold; margin-bottom:2px;">
                            ${tumor.name}
                        </div>
                        <div style="color:#cccccc; font-size:10px;">
                            ${tumor.description}
                        </div>
                    </div>

                    <div style="background:rgba(0,217,255,0.1); padding:6px 10px;
                                border-radius:6px; border:1px solid rgba(0,217,255,0.3);">
                        <div style="color:#00d9ff; font-size:10px; font-weight:bold;">
                            Drag to rotate
                        </div>
                    </div>
                </div>

                <!-- Decorative scan lines -->
                <div style="position:absolute; top:0; left:0; right:0; bottom:0;
                            background:repeating-linear-gradient(0deg,
                                transparent, transparent 2px,
                                rgba(0,217,255,0.02) 2px,
                                rgba(0,217,255,0.02) 4px);
                            pointer-events:none;"></div>

                <!-- Corner brackets -->
                <div style="position:absolute; top:50px; left:30px;
                            width:20px; height:20px;
                            border-left:2px solid #00d9ff;
                            border-top:2px solid #00d9ff;"></div>
                <div style="position:absolute; top:50px; right:30px;
                            width:20px; height:20px;
                            border-right:2px solid #00d9ff;
                            border-top:2px solid #00d9ff;"></div>
                <div style="position:absolute; bottom:50px; left:30px;
                            width:20px; height:20px;
                            border-left:2px solid #00d9ff;
                            border-bottom:2px solid #00d9ff;"></div>
                <div style="position:absolute; bottom:50px; right:30px;
                            width:20px; height:20px;
                            border-right:2px solid #00d9ff;
                            border-bottom:2px solid #00d9ff;"></div>
            </div>
        `;

        container.innerHTML = html;

        // Add 3D rotation effect
        var wrapper = document.getElementById('brain-wrapper');
        var svg = document.getElementById('brain-svg');
        var isDragging = false;
        var startX = 0, startY = 0;
        var rotY = 0, rotX = 0;

        wrapper.style.cursor = 'grab';

        wrapper.addEventListener('mousedown', function(e) {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            wrapper.style.cursor = 'grabbing';
        });

        wrapper.addEventListener('mousemove', function(e) {
            if (isDragging) {
                rotY += (e.clientX - startX) * 0.5;
                rotX -= (e.clientY - startY) * 0.5;
                rotX = Math.max(-30, Math.min(30, rotX));
                svg.style.transform = 'rotateY(' + rotY + 'deg) rotateX(' + rotX + 'deg)';
                startX = e.clientX;
                startY = e.clientY;
            }
        });

        wrapper.addEventListener('mouseup', function() {
            isDragging = false;
            wrapper.style.cursor = 'grab';
        });

        wrapper.addEventListener('mouseleave', function() {
            isDragging = false;
            wrapper.style.cursor = 'grab';
        });

        // Auto rotate
        var autoRotate = 0;
        setInterval(function() {
            if (!isDragging) {
                autoRotate += 0.3;
                svg.style.transform = 'rotateY(' + autoRotate + 'deg)';
            }
        }, 50);
    }
};