const navButtons = document.querySelectorAll('.top-buttons a');
const panels = document.querySelectorAll('.content-panel');

navButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
        event.preventDefault();

        navButtons.forEach((btn) => btn.classList.remove('active'));
        button.classList.add('active');

        const targetId = button.getAttribute('data-target');
        panels.forEach((panel) => {
            panel.classList.toggle('active', panel.id === targetId);
        });
    });
});

window.addEventListener('load', () => {
    document.body.classList.add('loaded');
    initQuoteRequest();
});

// ============== ML Model Webcam Detection ==============

const trashTypes = ['Plastic Bottle', 'Paper Cup', 'Metal Can', 'Plastic Bag', 'Cardboard', 'Glass Bottle', 'Food Waste', 'Styrofoam'];
let stream = null;
let detectionActive = false;
let frameCount = 0;

const startWebcamBtn = document.getElementById('start-webcam-btn');
const stopWebcamBtn = document.getElementById('stop-webcam-btn');
const videoElement = document.getElementById('webcam-video');
const canvasElement = document.getElementById('detection-canvas');
const detectionStatus = document.getElementById('detection-status');
const detectionList = document.getElementById('detection-list');
const confidenceBar = document.getElementById('confidence-bar');
const confidenceValue = document.getElementById('confidence-value');

// Request camera access
startWebcamBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' },
            audio: false
        });
        videoElement.srcObject = stream;
        
        // Wait for video to load
        videoElement.onloadedmetadata = () => {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
            detectionActive = true;
            startWebcamBtn.classList.add('hidden');
            stopWebcamBtn.classList.remove('hidden');
            detectionStatus.textContent = '🟢 Camera Active - Scanning...';
            runDetection();
        };
    } catch (error) {
        if (error.name === 'NotAllowedError') {
            detectionStatus.textContent = '❌ Camera access denied. Please allow camera permissions.';
        } else if (error.name === 'NotFoundError') {
            detectionStatus.textContent = '❌ No camera found on this device.';
        } else {
            detectionStatus.textContent = `❌ Error: ${error.message}`;
        }
    }
});

// Stop camera
stopWebcamBtn.addEventListener('click', () => {
    detectionActive = false;
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    videoElement.srcObject = null;
    startWebcamBtn.classList.remove('hidden');
    stopWebcamBtn.classList.add('hidden');
    detectionStatus.textContent = 'Ready to detect';
    
    // Clear canvas
    const ctx = canvasElement.getContext('2d');
    ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    // Reset detection list
    detectionList.innerHTML = '<li class=\"placeholder\">No items detected yet</li>';
    confidenceBar.style.width = '0%';
    confidenceValue.textContent = '0%';
});

// Simulated ML Detection Function
function runDetection() {
    if (!detectionActive) return;

    frameCount++;
    const ctx = canvasElement.getContext('2d');

    // Draw video frame to canvas
    ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

    // Simulated detection - randomly detect items with varying confidence
    if (frameCount % 15 === 0) {
        const detectedItems = [];
        
        // 70% chance to detect something
        if (Math.random() > 0.3) {
            // Number of items to detect
            const numItems = Math.floor(Math.random() * 3) + 1;
            
            for (let i = 0; i < numItems; i++) {
                const trashType = trashTypes[Math.floor(Math.random() * trashTypes.length)];
                const confidence = Math.random() * 0.4 + 0.6; // 60-100% confidence
                
                detectedItems.push({
                    type: trashType,
                    confidence: confidence,
                    x: Math.random() * (canvasElement.width - 100),
                    y: Math.random() * (canvasElement.height - 100),
                    width: 80 + Math.random() * 80,
                    height: 60 + Math.random() * 80
                });
            }
            
            // Draw bounding boxes
            detectedItems.forEach(item => {
                // Draw box with glow effect
                ctx.strokeStyle = `rgba(31, 143, 95, 0.9)`;
                ctx.lineWidth = 3;
                ctx.shadowColor = 'rgba(31, 143, 95, 0.6)';
                ctx.shadowBlur = 15;
                ctx.strokeRect(item.x, item.y, item.width, item.height);
                ctx.shadowBlur = 0;
                
                // Draw label background
                const label = `${item.type} ${(item.confidence * 100).toFixed(0)}%`;
                ctx.font = 'bold 14px Arial';
                ctx.fillStyle = 'rgba(31, 143, 95, 0.9)';
                const textMetrics = ctx.measureText(label);
                ctx.fillRect(item.x, item.y - 25, textMetrics.width + 10, 20);
                
                // Draw label text
                ctx.fillStyle = 'white';
                ctx.fillText(label, item.x + 5, item.y - 8);
            });
            
            // Update detection list
            updateDetectionList(detectedItems);
            
            // Update confidence
            const avgConfidence = detectedItems.reduce((sum, item) => sum + item.confidence, 0) / detectedItems.length;
            updateConfidence(avgConfidence);
            
            detectionStatus.textContent = `🟢 Detected ${detectedItems.length} item(s)`;
        } else {
            detectionStatus.textContent = '🟢 Scanning... (no detections yet)';
            updateConfidence(0);
        }
    }

    requestAnimationFrame(runDetection);
}

// Update detection list
function updateDetectionList(items) {
    const uniqueItems = {};
    
    items.forEach(item => {
        if (uniqueItems[item.type]) {
            uniqueItems[item.type]++;
        } else {
            uniqueItems[item.type] = 1;
        }
    });
    
    let html = '';
    for (const [type, count] of Object.entries(uniqueItems)) {
        html += `<li class=\"detection-item\"><span class=\"item-badge\">${count}</span> ${type}</li>`;
    }
    
    detectionList.innerHTML = html;
}

// Update confidence meter
function updateConfidence(confidence) {
    const percentage = Math.round(confidence * 100);
    confidenceBar.style.width = percentage + '%';
    confidenceValue.textContent = percentage + '%';
}

// ============== Quote Request UI ==============

const authOpenBtn = document.getElementById('auth-open-btn');
const authCloseBtn = document.getElementById('auth-close-btn');
const authModal = document.getElementById('auth-modal');
const authForm = document.getElementById('auth-form');
const authMessage = document.getElementById('auth-message');

function initQuoteRequest() {
    authOpenBtn?.addEventListener('click', openQuoteModal);
    authCloseBtn?.addEventListener('click', closeQuoteModal);

    authForm?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const data = new FormData(authForm);
        const payload = {
            name: String(data.get('name') || '').trim(),
            email: String(data.get('email') || '').trim(),
            company: String(data.get('company') || '').trim(),
            message: String(data.get('message') || '').trim(),
        };

        if (!payload.name || !payload.email || !payload.message) {
            authMessage.textContent = 'Please fill in your name, email, and message.';
            return;
        }

        await submitQuoteRequest(payload);
    });
}

function openQuoteModal() {
    authModal.classList.remove('hidden');
    authModal.setAttribute('aria-hidden', 'false');
    authForm.reset();
    authMessage.textContent = '';
}

function closeQuoteModal() {
    authModal.classList.add('hidden');
    authModal.setAttribute('aria-hidden', 'true');
}

async function submitQuoteRequest(payload) {
    try {
        const response = await fetch('/api/quote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok || !data.ok) {
            authMessage.textContent = data.error || 'Unable to send quote request.';
            authMessage.classList.add('error');
            return;
        }

        authMessage.textContent = 'Thanks! Your quote request was sent successfully.';
        authMessage.classList.remove('error');
        authForm.reset();
    } catch (error) {
        authMessage.textContent = 'Network error: could not send request.';
        authMessage.classList.add('error');
    }
}

