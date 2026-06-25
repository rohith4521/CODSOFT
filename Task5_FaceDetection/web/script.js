// State variables
let currentMode = 'webcam'; // 'webcam' or 'upload'
let webcamStream = null;
let scanIntervalId = null;
let currentFrameBase64 = null;
let selectedCropForRegister = null;

// DOM Elements
const btnWebcamMode = document.getElementById('btn-webcam-mode');
const btnUploadMode = document.getElementById('btn-upload-mode');
const feedTitle = document.getElementById('feed-title');
const feedBadge = document.getElementById('feed-badge');

const webcamFeed = document.getElementById('webcam-feed');
const uploadZone = document.getElementById('upload-zone');
const imageInput = document.getElementById('image-input');
const processedFrame = document.getElementById('processed-frame');
const detectedFacesList = document.getElementById('detected-faces-list');
const btnTriggerScan = document.getElementById('btn-trigger-scan');
const feedHelpText = document.getElementById('feed-help-text');

const registeredProfilesList = document.getElementById('registered-profiles-list');
const profilesCountBadge = document.getElementById('profiles-count-badge');

// Modal Elements
const registerModal = document.getElementById('register-modal');
const modalCropImg = document.getElementById('modal-crop-img');
const registerNameInput = document.getElementById('register-name-input');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelRegister = document.getElementById('btn-cancel-register');
const btnSubmitRegister = document.getElementById('btn-submit-register');

// Hidden canvas for frame capturing
const captureCanvas = document.createElement('canvas');
const captureContext = captureCanvas.getContext('2d');
captureCanvas.width = 640;
captureCanvas.height = 480;

// Initialize
async function initDashboard() {
    await fetchProfiles();
    switchMode('webcam');
}

// Fetch registered faces profiles
async function fetchProfiles() {
    try {
        const res = await fetch('/api/profiles');
        const data = await res.json();
        renderProfiles(data.profiles || []);
    } catch (e) {
        console.error("Error fetching profiles:", e);
    }
}

function renderProfiles(profiles) {
    profilesCountBadge.innerText = `${profiles.length} Profile${profiles.length !== 1 ? 's' : ''}`;
    
    if (profiles.length === 0) {
        registeredProfilesList.innerHTML = `
            <div class="empty-state">
                <p>No faces registered yet. Register faces via scanner options!</p>
            </div>
        `;
        return;
    }

    registeredProfilesList.innerHTML = '';
    profiles.forEach(p => {
        const card = document.createElement('div');
        card.className = 'profile-card';
        card.innerHTML = `
            <img class="profile-img" src="${p.img}" alt="${p.name}">
            <span class="profile-name">${p.name}</span>
        `;
        registeredProfilesList.appendChild(card);
    });
}

// Mode switching
btnWebcamMode.addEventListener('click', () => switchMode('webcam'));
btnUploadMode.addEventListener('click', () => switchMode('upload'));

function switchMode(mode) {
    currentMode = mode;
    resetState();

    if (mode === 'webcam') {
        btnWebcamMode.classList.add('active');
        btnUploadMode.classList.remove('active');
        feedTitle.innerText = 'Live Video Input';
        feedBadge.innerText = 'Webcam active';
        feedBadge.className = 'badge active';
        
        webcamFeed.style.display = 'block';
        uploadZone.style.display = 'none';
        btnTriggerScan.style.display = 'none';
        feedHelpText.innerText = 'Live scanner automatically processes frames every 500ms.';
        
        startWebcam();
    } else {
        btnUploadMode.classList.add('active');
        btnWebcamMode.classList.remove('active');
        feedTitle.innerText = 'Static Image Input';
        feedBadge.innerText = 'Waiting for file';
        feedBadge.className = 'badge';
        
        webcamFeed.style.display = 'none';
        uploadZone.style.display = 'flex';
        btnTriggerScan.style.display = 'block';
        btnTriggerScan.setAttribute('disabled', 'true');
        feedHelpText.innerText = 'Upload an image and click Analyze to scan.';
        
        stopWebcam();
    }
}

// Reset scan UI state
function resetState() {
    currentFrameBase64 = null;
    const blankSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='480'><rect width='640' height='480' fill='%230b0e14'/><text x='50%25' y='50%25' font-family='sans-serif' font-size='18' fill='%23a0aec0' dominant-baseline='middle' text-anchor='middle'>Camera feed placeholder</text></svg>";
    processedFrame.src = blankSvg;
    detectedFacesList.innerHTML = '<p class="placeholder-text">Scanning for faces...</p>';
}

// Webcam stream controls
async function startWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 },
            audio: false
        });
        webcamFeed.srcObject = webcamStream;
        
        // Start processing interval
        scanIntervalId = setInterval(captureWebcamFrame, 500);
    } catch (e) {
        console.error("Camera access denied or unavailable:", e);
        feedBadge.innerText = 'Webcam offline';
        feedBadge.className = 'badge';
        feedHelpText.innerText = 'Webcam access failed. Switch to Image Upload mode.';
    }
}

function stopWebcam() {
    if (scanIntervalId) {
        clearInterval(scanIntervalId);
        scanIntervalId = null;
    }
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    webcamFeed.srcObject = null;
}

// Webcam frame capturing routine
async function captureWebcamFrame() {
    if (!webcamStream || webcamFeed.paused || webcamFeed.ended) return;
    
    // Draw mirrored video frame to canvas
    captureContext.save();
    captureContext.translate(640, 0);
    captureContext.scale(-1, 1);
    captureContext.drawImage(webcamFeed, 0, 0, 640, 480);
    captureContext.restore();
    
    const frameB64 = captureCanvas.toDataURL('image/jpeg', 0.85);
    sendScanRequest(frameB64);
}

// Send base64 frame to backend face detector API
async function sendScanRequest(frameB64) {
    try {
        const res = await fetch('/api/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: frameB64 })
        });
        const data = await res.json();
        
        if (data.error) {
            console.error(data.error);
            return;
        }

        // Draw overall image
        processedFrame.src = data.frame;
        renderDetectedFaces(data.faces);
    } catch (e) {
        console.error("Face detection API error:", e);
    }
}

// Render detected faces rows
function renderDetectedFaces(faces) {
    if (!faces || faces.length === 0) {
        detectedFacesList.innerHTML = '<p class="placeholder-text">Scanning for faces...</p>';
        return;
    }

    detectedFacesList.innerHTML = '';
    faces.forEach((face, index) => {
        const row = document.createElement('div');
        row.className = 'detected-face-row';
        
        const isKnown = face.name !== 'Unknown';
        const nameClass = isKnown ? 'known' : '';
        const confidencePercent = Math.round(face.confidence * 100);
        
        let actionBtnHtml = '';
        if (!isKnown) {
            actionBtnHtml = `<button class="btn btn-primary btn-small" onclick="openRegisterModal('${face.crop_b64}')">Register</button>`;
        } else {
            actionBtnHtml = `<span class="badge active" style="font-size:0.6rem;">Match</span>`;
        }

        row.innerHTML = `
            <div class="detected-face-info">
                <img class="face-mini-crop" src="${face.crop_b64}" alt="Face crop">
                <div class="face-text">
                    <span class="face-name ${nameClass}">${face.name}</span>
                    <span class="face-confidence">${isKnown ? `Confidence: ${confidencePercent}%` : 'Not recognized'}</span>
                </div>
            </div>
            ${actionBtnHtml}
        `;
        
        detectedFacesList.appendChild(row);
    });
}

// File Input Listeners
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        // Clear previous results and set waiting state
        detectedFacesList.innerHTML = '<p class="placeholder-text">Waiting for analysis...</p>';
        const reader = new FileReader();
        reader.onload = (event) => {
            currentFrameBase64 = event.target.result;
            processedFrame.src = currentFrameBase64;
            btnTriggerScan.removeAttribute('disabled');
            feedBadge.innerText = 'File loaded';
            feedBadge.className = 'badge active';
        };
        reader.readAsDataURL(file);
    }
});

btnTriggerScan.addEventListener('click', () => {
    if (currentFrameBase64) {
        sendScanRequest(currentFrameBase64);
    }
});

// Modal Operations
window.openRegisterModal = function(cropB64) {
    // Stop live scanner temporarily to lock frame
    if (scanIntervalId) {
        clearInterval(scanIntervalId);
        scanIntervalId = null;
    }

    selectedCropForRegister = cropB64;
    modalCropImg.src = cropB64;
    registerNameInput.value = '';
    registerModal.style.display = 'flex';
};

function closeModal() {
    registerModal.style.display = 'none';
    selectedCropForRegister = null;
    
    // Restart live scanner if in webcam mode
    if (currentMode === 'webcam' && !scanIntervalId) {
        scanIntervalId = setInterval(captureWebcamFrame, 500);
    }
}

btnCloseModal.addEventListener('click', closeModal);
btnCancelRegister.addEventListener('click', closeModal);

btnSubmitRegister.addEventListener('click', async () => {
    const name = registerNameInput.value.trim();
    if (!name) {
        alert('Please enter a name for the profile.');
        return;
    }

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, crop: selectedCropForRegister })
        });
        const data = await res.json();
        
        if (data.success) {
            closeModal();
            await fetchProfiles();
        } else {
            alert('Failed to register face: ' + data.error);
        }
    } catch (e) {
        console.error("Error registering profile:", e);
        alert('Registration failed due to network error.');
    }
});

// Cleanup webcam on page close
window.addEventListener('beforeunload', stopWebcam);

// Run initial configurations
initDashboard();
