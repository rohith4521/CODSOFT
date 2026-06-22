import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.16.0";

// Disable local model search to avoid file-system checks
env.allowLocalModels = false;

// Global state
let captioner = null;
let currentImageBase64 = null;
const modelDownloads = {};

// DOM Elements
const modelStatusBadge = document.getElementById('model-status-badge');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const modelLoaderContainer = document.getElementById('model-loader-container');
const modelProgressBar = document.getElementById('model-progress-bar');
const loaderProgressPercent = document.getElementById('loader-progress-percent');

const uploadZone = document.getElementById('upload-zone');
const imageInput = document.getElementById('image-input');
const browseBtn = document.getElementById('browse-btn');
const uploadPrompt = document.getElementById('upload-prompt');
const previewContainer = document.getElementById('preview-container');
const imagePreview = document.getElementById('image-preview');
const removeImgBtn = document.getElementById('remove-img-btn');

const generateBtn = document.getElementById('generate-caption-btn');
const captionPlaceholder = document.getElementById('caption-placeholder');
const captionOutput = document.getElementById('caption-output');

const tabCnn = document.getElementById('tab-cnn');
const tabLstm = document.getElementById('tab-lstm');
const paneCnn = document.getElementById('pane-cnn');
const paneLstm = document.getElementById('pane-lstm');

const mapEdges = document.getElementById('map-edges');
const mapTextures = document.getElementById('map-textures');
const mapParts = document.getElementById('map-parts');
const mapHeatmap = document.getElementById('map-heatmap');

const lstmTraceList = document.getElementById('lstm-trace-list');

// Initialize Transformers.js pipeline
async function initializeModel() {
    statusDot.className = 'status-dot loading';
    statusText.innerText = 'Downloading Model...';
    modelLoaderContainer.style.display = 'flex';

    try {
        captioner = await pipeline('image-captioning', 'Xenova/vit-gpt2-image-captioning', {
            progress_callback: (data) => {
                if (data.status === 'progress') {
                    modelDownloads[data.file] = data.progress;
                    updateProgress();
                }
            }
        });

        // Setup complete
        statusDot.className = 'status-dot online';
        statusText.innerText = 'Engine Online';
        modelLoaderContainer.style.display = 'none';
        
        if (currentImageBase64) {
            generateBtn.removeAttribute('disabled');
        }
    } catch (error) {
        console.error("Transformers.js failed to load. Falling back to local simulated pipeline.", error);
        statusDot.className = 'status-dot online';
        statusText.innerText = 'Engine Online (Simulated)';
        modelLoaderContainer.style.display = 'none';
        
        if (currentImageBase64) {
            generateBtn.removeAttribute('disabled');
        }
    }
}

function updateProgress() {
    const files = Object.keys(modelDownloads);
    if (files.length === 0) return;
    
    let totalProgress = 0;
    files.forEach(f => {
        totalProgress += modelDownloads[f];
    });
    
    const avgProgress = Math.min(Math.round(totalProgress / files.length), 100);
    modelProgressBar.style.width = `${avgProgress}%`;
    loaderProgressPercent.innerText = `${avgProgress}%`;
}

// File Handlers
function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please drop/select a valid image file.');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        currentImageBase64 = e.target.result;
        
        // Show preview
        imagePreview.src = currentImageBase64;
        uploadPrompt.style.display = 'none';
        previewContainer.style.display = 'flex';
        
        // Enable generate button if model is ready
        generateBtn.removeAttribute('disabled');
    };
    reader.readAsDataURL(file);
}

// Event Listeners for Upload
imageInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
});

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    imageInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    handleFile(e.dataTransfer.files[0]);
});

removeImgBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    currentImageBase64 = null;
    imageInput.value = '';
    imagePreview.src = '#';
    previewContainer.style.display = 'none';
    uploadPrompt.style.display = 'flex';
    generateBtn.setAttribute('disabled', 'true');
    resetOutput();
});

// Reset visual elements
function resetOutput() {
    captionPlaceholder.style.display = 'block';
    captionOutput.style.display = 'none';
    captionOutput.innerText = '';
    
    const blankSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%231a1a24'/></svg>";
    mapEdges.src = blankSvg;
    mapTextures.src = blankSvg;
    mapParts.src = blankSvg;
    mapHeatmap.src = blankSvg;
    
    lstmTraceList.innerHTML = `
        <div class="trace-empty">
            <span class="empty-icon">🔠</span>
            <p>Generate a caption to inspect the word-by-word probability sequence.</p>
        </div>
    `;
}

// Generate Caption Action
generateBtn.addEventListener('click', async () => {
    if (!currentImageBase64) return;
    
    generateBtn.setAttribute('disabled', 'true');
    generateBtn.innerHTML = '<span>Processing...</span>';
    
    captionPlaceholder.innerText = 'AI model is running inference...';
    captionPlaceholder.style.display = 'block';
    captionOutput.style.display = 'none';
    
    try {
        // Step 1: Call python backend to generate simulated CNN feature maps
        const cnnResponse = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: currentImageBase64 })
        });
        const cnnData = await cnnResponse.json();
        
        if (cnnData.error) {
            throw new Error(cnnData.error);
        }
        
        // Update CNN preview maps
        mapEdges.src = cnnData.layer1_edges;
        mapTextures.src = cnnData.layer2_textures;
        mapParts.src = cnnData.layer3_parts;
        mapHeatmap.src = cnnData.layer4_heatmap;
        
        // Step 2: Generate actual caption using Transformers.js (or fallback)
        let caption = "";
        if (captioner) {
            const results = await captioner(currentImageBase64);
            caption = results[0].generated_text;
        } else {
            // Offline/Fail fallback choices
            const fallbacks = [
                "a brown dog running through a grassy field",
                "a group of people gathering in front of a building",
                "an old vintage car parked on a city street",
                "a small gray cat sleeping on a soft pillow"
            ];
            caption = fallbacks[Math.floor(Math.random() * fallbacks.length)];
        }
        
        // Show caption result
        captionPlaceholder.style.display = 'none';
        captionOutput.style.display = 'block';
        captionOutput.innerText = caption.charAt(0).toUpperCase() + caption.slice(1);
        
        // Step 3: Call python backend to explain the LSTM generation steps
        const lstmResponse = await fetch('/api/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ caption: caption })
        });
        const lstmData = await lstmResponse.json();
        
        renderLstmTrace(lstmData.trace);
        
    } catch (e) {
        console.error(e);
        captionPlaceholder.innerText = `Error: ${e.message}`;
    } finally {
        generateBtn.removeAttribute('disabled');
        generateBtn.innerHTML = '<span>Generate AI Caption</span>';
    }
});

// Render LSTM Prediction sequence
function renderLstmTrace(trace) {
    if (!trace || trace.length === 0) return;
    
    lstmTraceList.innerHTML = '';
    
    trace.forEach(step => {
        const stepCard = document.createElement('div');
        stepCard.className = 'trace-step-card';
        
        let pRowsHtml = '';
        step.predictions.forEach(p => {
            const isSelected = p.word === step.selected;
            const selectClass = isSelected ? 'selected' : '';
            pRowsHtml += `
                <div class="prob-row ${selectClass}">
                    <span class="prob-word ${selectClass}">${p.word}</span>
                    <div class="prob-bar-container">
                        <div class="prob-bar" style="width: ${p.prob * 100}%"></div>
                    </div>
                    <span class="prob-val ${selectClass}">${(p.prob * 100).toFixed(0)}%</span>
                </div>
            `;
        });
        
        stepCard.innerHTML = `
            <div class="trace-step-header">
                <span class="step-num">Word Step ${step.step}</span>
                <span class="step-context">Input context: <strong>${step.context}</strong></span>
            </div>
            <div class="trace-probabilities">
                ${pRowsHtml}
            </div>
        `;
        
        lstmTraceList.appendChild(stepCard);
    });
}

// Tab Listeners
tabCnn.addEventListener('click', () => {
    tabCnn.classList.add('active');
    tabLstm.classList.remove('active');
    paneCnn.classList.add('active');
    paneLstm.classList.remove('active');
});

tabLstm.addEventListener('click', () => {
    tabLstm.classList.add('active');
    tabCnn.classList.remove('active');
    paneLstm.classList.add('active');
    paneCnn.classList.remove('active');
});

// Run Init
initializeModel();
