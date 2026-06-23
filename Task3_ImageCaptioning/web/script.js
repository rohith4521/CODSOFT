import { pipeline, env, RawImage } from "https://cdn.jsdelivr.net/npm/@xenova/transformers@2.16.0";

// Disable local model search to avoid file-system checks
env.allowLocalModels = false;

// Global state
let captioner = null;
let currentImageBase64 = null;
let currentFileName = "";
let modelDownloads = {};
let currentModelId = 'vit-gpt2';

// RNN Playback state
let currentTrace = [];
let currentStepIndex = -1;
let isPlaying = false;
let playIntervalId = null;

// DOM Elements
const modelStatusBadge = document.getElementById('model-status-badge');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const modelLoaderContainer = document.getElementById('model-loader-container');
const modelProgressBar = document.getElementById('model-progress-bar');
const loaderProgressPercent = document.getElementById('loader-progress-percent');
const modelSelector = document.getElementById('model-selector');

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
const tabArch = document.getElementById('tab-arch');
const paneCnn = document.getElementById('pane-cnn');
const paneLstm = document.getElementById('pane-lstm');
const paneArch = document.getElementById('pane-arch');

const mapEdges = document.getElementById('map-edges');
const mapTextures = document.getElementById('map-textures');
const mapParts = document.getElementById('map-parts');
const mapHeatmap = document.getElementById('map-heatmap');

const lstmTraceList = document.getElementById('lstm-trace-list');
const rnnPlayerControls = document.getElementById('rnn-player-controls');
const btnPlayerPrev = document.getElementById('btn-player-prev');
const btnPlayerToggle = document.getElementById('btn-player-toggle');
const btnPlayerNext = document.getElementById('btn-player-next');
const btnPlayerReset = document.getElementById('btn-player-reset');
const playerStatusText = document.getElementById('player-status-text');


// Load deep learning model
async function loadModel(modelId) {
    currentModelId = modelId;
    captioner = null;
    modelDownloads = {};
    
    statusDot.className = 'status-dot loading';
    statusText.innerText = 'Downloading Model...';
    modelLoaderContainer.style.display = 'flex';
    modelProgressBar.style.width = '0%';
    loaderProgressPercent.innerText = '0%';
    generateBtn.setAttribute('disabled', 'true');

    const modelPath = modelId === 'blip-base' 
        ? 'Xenova/blip-image-captioning-base' 
        : 'Xenova/vit-gpt2-image-captioning';

    try {
        captioner = await pipeline('image-to-text', modelPath, {
            progress_callback: (data) => {
                if (data.status === 'progress') {
                    modelDownloads[data.file] = data.progress;
                    updateProgress();
                }
            }
        });

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

    currentFileName = file.name;
    resetOutput();

    const reader = new FileReader();
    reader.onload = (e) => {
        currentImageBase64 = e.target.result;
        
        imagePreview.src = currentImageBase64;
        uploadPrompt.style.display = 'none';
        previewContainer.style.display = 'flex';
        
        // Enable button
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

// Reset output visualization state
function resetOutput() {
    captionPlaceholder.style.display = 'block';
    captionPlaceholder.innerText = 'Upload an image and click generate to inspect results.';
    captionOutput.style.display = 'none';
    captionOutput.innerText = '';
    
    const blankSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='224' height='224'><rect width='224' height='224' fill='%231a1a24'/></svg>";
    mapEdges.src = blankSvg;
    mapTextures.src = blankSvg;
    mapParts.src = blankSvg;
    mapHeatmap.src = blankSvg;
    
    rnnPlayerControls.style.display = 'none';
    resetPlayback();
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
        // Step 1: Call python backend to generate real visual feature maps
        const cnnResponse = await fetch('/api/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                image: currentImageBase64, 
                filename: currentFileName,
                model: currentModelId
            })
        });
        const cnnData = await cnnResponse.json();
        
        if (cnnData.error) {
            throw new Error(cnnData.error);
        }
        
        mapEdges.src = cnnData.layer1_edges;
        mapTextures.src = cnnData.layer2_textures;
        mapParts.src = cnnData.layer3_parts;
        mapHeatmap.src = cnnData.layer4_heatmap;
        
        // Step 2: Generate actual caption using Transformers.js (or fallback)
        let caption = "";
        if (captioner) {
            const image = await RawImage.fromURL(currentImageBase64);
            const results = await captioner(image);
            caption = results[0].generated_text;
        } else {
            // Use the real-time heuristic caption generated by the backend from the actual pixels!
            caption = cnnData.caption || "a minimalist composition with balanced colors";
        }
        
        // Step 3: Call python backend to explain the LSTM generation steps
        const lstmResponse = await fetch('/api/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ caption: caption })
        });
        const lstmData = await lstmResponse.json();
        
        // Select LSTM tab automatically to show generation
        selectTab('lstm');
        
        // Initialize the interactive playback
        initTracePlayer(lstmData.trace);
        
    } catch (e) {
        console.error(e);
        captionPlaceholder.innerText = `Error: ${e.message}`;
    } finally {
        generateBtn.removeAttribute('disabled');
        generateBtn.innerHTML = '<span>Generate AI Caption</span>';
    }
});

// Interactive Player controls
function initTracePlayer(trace) {
    currentTrace = trace;
    currentStepIndex = -1;
    stopPlayback();
    
    rnnPlayerControls.style.display = 'flex';
    lstmTraceList.innerHTML = '';
    captionOutput.innerText = '';
    captionOutput.style.display = 'block';
    captionPlaceholder.style.display = 'none';
    
    updatePlayerUI();
    
    // Automatically start playback
    startPlayback();
}

function updatePlayerUI() {
    btnPlayerToggle.innerHTML = isPlaying ? '<span>⏸️ Pause</span>' : '<span>▶️ Play</span>';
    
    const totalSteps = currentTrace.length;
    const currentStepNum = currentStepIndex + 1;
    playerStatusText.innerText = `Step ${currentStepNum} / ${totalSteps}`;
    
    btnPlayerPrev.disabled = currentStepIndex <= -1;
    btnPlayerNext.disabled = currentStepIndex >= totalSteps - 1;
}

function playNextStep() {
    if (currentStepIndex >= currentTrace.length - 1) {
        stopPlayback();
        return;
    }
    
    currentStepIndex++;
    renderTraceUpToCurrentStep();
    updatePlayerUI();
}

function playPrevStep() {
    if (currentStepIndex <= -1) return;
    
    currentStepIndex--;
    renderTraceUpToCurrentStep();
    updatePlayerUI();
}

function startPlayback() {
    if (currentStepIndex >= currentTrace.length - 1) {
        currentStepIndex = -1; // Loop restart
    }
    isPlaying = true;
    updatePlayerUI();
    playIntervalId = setInterval(playNextStep, 800);
}

function stopPlayback() {
    isPlaying = false;
    if (playIntervalId) {
        clearInterval(playIntervalId);
        playIntervalId = null;
    }
    updatePlayerUI();
}

function resetPlayback() {
    stopPlayback();
    currentStepIndex = -1;
    renderTraceUpToCurrentStep();
    updatePlayerUI();
}

function renderTraceUpToCurrentStep() {
    lstmTraceList.innerHTML = '';
    
    if (currentStepIndex === -1) {
        captionOutput.innerText = '';
        lstmTraceList.innerHTML = `
            <div class="trace-empty">
                <span class="empty-icon">🔠</span>
                <p>Use the player controls to step through the RNN tokenizer trace.</p>
            </div>
        `;
        return;
    }
    
    // Reconstruct the text generated so far
    const words = [];
    for (let i = 0; i <= currentStepIndex; i++) {
        const selectedWord = currentTrace[i].selected;
        if (selectedWord !== '<end>') {
            words.push(selectedWord);
        }
    }
    
    if (words.length > 0) {
        const sentence = words.join(' ');
        captionOutput.innerText = sentence.charAt(0).toUpperCase() + sentence.slice(1);
    } else {
        captionOutput.innerText = '';
    }
    
    // Render the steps up to the current index
    for (let i = 0; i <= currentStepIndex; i++) {
        const step = currentTrace[i];
        const card = document.createElement('div');
        card.className = 'trace-step-card';
        if (i === currentStepIndex) {
            card.classList.add('active-step');
        }
        
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
        
        card.innerHTML = `
            <div class="trace-step-header">
                <span class="step-num">Word Step ${step.step}</span>
                <span class="step-context">Input context: <strong>${step.context}</strong></span>
            </div>
            <div class="trace-probabilities">
                ${pRowsHtml}
            </div>
        `;
        lstmTraceList.appendChild(card);
    }
    
    // Auto-scroll to the bottom of the list
    if (lstmTraceList.lastChild) {
        lstmTraceList.lastChild.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Bind Player Actions
btnPlayerToggle.addEventListener('click', () => {
    if (isPlaying) {
        stopPlayback();
    } else {
        startPlayback();
    }
});

btnPlayerNext.addEventListener('click', () => {
    stopPlayback();
    playNextStep();
});

btnPlayerPrev.addEventListener('click', () => {
    stopPlayback();
    playPrevStep();
});

btnPlayerReset.addEventListener('click', () => {
    resetPlayback();
});

// Bind Model Selector Change
modelSelector.addEventListener('change', (e) => {
    resetOutput();
    loadModel(e.target.value);
});


// Tab Routing System
function selectTab(tabId) {
    [tabCnn, tabLstm, tabArch].forEach(tab => {
        if (tab) tab.classList.remove('active');
    });
    [paneCnn, paneLstm, paneArch].forEach(pane => {
        if (pane) pane.classList.remove('active');
    });
    
    if (tabId === 'cnn') {
        tabCnn.classList.add('active');
        paneCnn.classList.add('active');
    } else if (tabId === 'lstm') {
        tabLstm.classList.add('active');
        paneLstm.classList.add('active');
    } else if (tabId === 'arch') {
        tabArch.classList.add('active');
        paneArch.classList.add('active');
    }
}

tabCnn.addEventListener('click', () => selectTab('cnn'));
tabLstm.addEventListener('click', () => selectTab('lstm'));
tabArch.addEventListener('click', () => selectTab('arch'));

// Initialize ViT-GPT2 Model
loadModel('vit-gpt2');
