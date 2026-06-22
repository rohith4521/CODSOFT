// State variables
let allMovies = [];
let allBooks = [];
let allItems = [];
let usersList = [];
let userRatings = {};

// DOM elements - Navigation
const btnModeContent = document.getElementById('btn-mode-content');
const btnModeCollab = document.getElementById('btn-mode-collab');
const sectionContent = document.getElementById('section-content');
const sectionCollab = document.getElementById('section-collab');

// DOM elements - Content-Based
const contentSelect = document.getElementById('content-item-select');
const selectedItemCard = document.getElementById('selected-item-card');
const selectedItemIcon = document.getElementById('selected-item-icon');
const selectedItemTitle = document.getElementById('selected-item-title');
const selectedItemGenre = document.getElementById('selected-item-genre');
const selectedItemDesc = document.getElementById('selected-item-desc');
const contentRecsContainer = document.getElementById('content-recs-container');
const contentMathPanel = document.getElementById('content-math-panel');
const contentMathTbody = document.getElementById('content-math-tbody');

// DOM elements - Collaborative
const collabSelect = document.getElementById('collab-user-select');
const userRatingsList = document.getElementById('user-ratings-list');
const collabRecsContainer = document.getElementById('collab-recs-container');
const collabMathPanel = document.getElementById('collab-math-panel');
const peerSimilaritiesGrid = document.getElementById('peer-similarities-grid');

// Tab toggling
btnModeContent.addEventListener('click', () => {
    btnModeContent.classList.add('active');
    btnModeCollab.classList.remove('active');
    sectionContent.classList.add('active');
    sectionCollab.classList.remove('active');
});

btnModeCollab.addEventListener('click', () => {
    btnModeCollab.classList.add('active');
    btnModeContent.classList.remove('active');
    sectionCollab.classList.add('active');
    sectionContent.classList.remove('active');
});

// Load DB elements
async function initializeDashboard() {
    try {
        // Fetch items
        const itemRes = await fetch('/api/items');
        const items = await itemRes.json();
        allMovies = items.movies || [];
        allBooks = items.books || [];
        allItems = [...allMovies, ...allBooks];
        
        populateItemSelect();
        
        // Fetch users
        const userRes = await fetch('/api/users');
        const usersData = await userRes.json();
        usersList = usersData.users || [];
        userRatings = usersData.ratings || {};
        
        populateUserSelect();
    } catch (e) {
        console.error("Error loading recommendation data:", e);
    }
}

// Populate dropdown for content items
function populateItemSelect() {
    contentSelect.innerHTML = '<option value="">-- Choose Movie or Book --</option>';
    
    // Add movies group
    const movieOptGroup = document.createElement('optgroup');
    movieOptGroup.label = 'Movies 🎬';
    allMovies.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.id;
        opt.innerText = m.title;
        movieOptGroup.appendChild(opt);
    });
    contentSelect.appendChild(movieOptGroup);

    // Add books group
    const bookOptGroup = document.createElement('optgroup');
    bookOptGroup.label = 'Books 📚';
    allBooks.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.id;
        opt.innerText = b.title;
        bookOptGroup.appendChild(opt);
    });
    contentSelect.appendChild(bookOptGroup);
}

// Populate dropdown for users
function populateUserSelect() {
    collabSelect.innerHTML = '<option value="">-- Choose User Profile --</option>';
    usersList.forEach(user => {
        const opt = document.createElement('option');
        opt.value = user;
        opt.innerText = user;
        collabSelect.appendChild(opt);
    });
}

// Handle Content Select Change
contentSelect.addEventListener('change', async () => {
    const item_id = contentSelect.value;
    if (!item_id) {
        selectedItemCard.style.display = 'none';
        contentMathPanel.style.display = 'none';
        contentRecsContainer.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📂</span>
                <p>Select an item on the left to generate recommendations.</p>
            </div>
        `;
        return;
    }

    // Display selected card details
    const selectedItem = allItems.find(item => item.id === item_id);
    selectedItemIcon.innerText = item_id.startsWith('m') ? '🎬' : '📚';
    selectedItemTitle.innerText = selectedItem.title;
    selectedItemGenre.innerText = selectedItem.genre;
    selectedItemDesc.innerText = selectedItem.desc;
    selectedItemCard.style.display = 'flex';

    try {
        const res = await fetch('/api/content', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id })
        });
        const data = await res.json();
        
        renderContentRecommendations(data.recommendations);
        renderContentMath(data.recommendations[0]?.id, data.explanation.math);
    } catch (e) {
        console.error(e);
    }
});

function renderContentRecommendations(recs) {
    if (!recs || recs.length === 0) {
        contentRecsContainer.innerHTML = '<p>No recommendations found.</p>';
        return;
    }

    contentRecsContainer.innerHTML = '';
    recs.forEach(rec => {
        const isMovie = rec.id.startsWith('m');
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.innerHTML = `
            <div class="item-icon-tag" style="width: 40px; height: 40px; font-size: 1.5rem;">
                ${isMovie ? '🎬' : '📚'}
            </div>
            <div class="rec-info">
                <div class="rec-title-row">
                    <span class="rec-title">${rec.title}</span>
                    <span class="genre-tag" style="font-size: 0.65rem;">${rec.genre}</span>
                </div>
                <p style="font-size: 0.75rem; color: var(--text-secondary); line-height: 1.3;">${rec.desc}</p>
            </div>
            <div class="rec-score-badge">
                <span class="rec-score-label">Similarity</span>
                <span class="rec-score-val">${rec.score.toFixed(3)}</span>
            </div>
        `;
        contentRecsContainer.appendChild(card);
    });
}

function renderContentMath(top_match_id, math_data) {
    if (!top_match_id || !math_data || !math_data[top_match_id]) {
        contentMathPanel.style.display = 'none';
        return;
    }

    const detail = math_data[top_match_id];
    contentMathPanel.style.display = 'flex';
    contentMathTbody.innerHTML = '';
    
    document.querySelector('.math-header p').innerText = `Checking word weights overlap between query and top match: "${detail.title}"`;

    if (!detail.overlap || detail.overlap.length === 0) {
        contentMathTbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No high weight word overlaps found. Genres do not share descriptive words.</td></tr>';
        return;
    }

    detail.overlap.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-family: monospace; font-weight:600; color: var(--accent-orange);">${row.term}</td>
            <td>${row.v1_val.toFixed(3)}</td>
            <td>${row.v2_val.toFixed(3)}</td>
            <td style="font-family: monospace; font-weight:700; color: var(--accent-green);">${row.product.toFixed(3)}</td>
        `;
        contentMathTbody.appendChild(tr);
    });
}

// Handle Collaborative User Change
collabSelect.addEventListener('change', async () => {
    const username = collabSelect.value;
    if (!username) {
        userRatingsList.innerHTML = '';
        collabRecsContainer.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">👥</span>
                <p>Select a user profile on the left to see collaborative recommendations.</p>
            </div>
        `;
        collabMathPanel.style.display = 'none';
        return;
    }

    await loadUserRecommendations(username);
});

async function loadUserRecommendations(username) {
    try {
        const res = await fetch('/api/collaborative', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await res.json();
        
        renderCollabRecommendations(data.recommendations);
        renderUserRatingsManager(username);
        renderCollabMath(data.explanation);
    } catch(e) {
        console.error(e);
    }
}

function renderCollabRecommendations(recs) {
    if (!recs || recs.length === 0) {
        collabRecsContainer.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">🏆</span>
                <p>This user has rated all items in the database! Edit ratings to test recommendations.</p>
            </div>
        `;
        return;
    }

    collabRecsContainer.innerHTML = '';
    recs.forEach(rec => {
        const isMovie = rec.id.startsWith('m');
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.innerHTML = `
            <div class="item-icon-tag" style="width: 40px; height: 40px; font-size: 1.5rem;">
                ${isMovie ? '🎬' : '📚'}
            </div>
            <div class="rec-info">
                <div class="rec-title-row">
                    <span class="rec-title">${rec.title}</span>
                    <span class="genre-tag" style="font-size: 0.65rem;">${rec.genre}</span>
                </div>
                <p style="font-size: 0.75rem; color: var(--text-secondary); line-height: 1.3;">${rec.desc}</p>
            </div>
            <div class="rec-score-badge rating">
                <span class="rec-score-label">Predicted</span>
                <span class="rec-score-val">★ ${rec.predicted_rating.toFixed(1)}</span>
            </div>
        `;
        collabRecsContainer.appendChild(card);
    });
}

function renderUserRatingsManager(username) {
    const ratings = userRatings[username] || {};
    userRatingsList.innerHTML = '';
    
    allItems.forEach(item => {
        const userRating = ratings[item.id] || 0;
        
        const row = document.createElement('div');
        row.className = 'rating-row-card';
        
        const label = userRating > 0 ? `${userRating} ★` : 'Unrated';
        const labelClass = userRating > 0 ? '' : 'unrated';
        
        row.innerHTML = `
            <span class="rating-row-title" title="${item.title}">${item.title}</span>
            <div class="rating-row-controls">
                <input type="range" min="0" max="5" value="${userRating}" class="rating-slider" data-item-id="${item.id}">
                <span class="rating-val-display ${labelClass}">${label}</span>
            </div>
        `;
        
        // Attach slide change event listener
        const slider = row.querySelector('.rating-slider');
        const display = row.querySelector('.rating-val-display');
        
        slider.addEventListener('input', (e) => {
            const val = parseInt(e.target.value);
            if (val === 0) {
                display.innerText = 'Unrated';
                display.className = 'rating-val-display unrated';
            } else {
                display.innerText = `${val} ★`;
                display.className = 'rating-val-display';
            }
        });
        
        slider.addEventListener('change', async (e) => {
            const item_id = e.target.getAttribute('data-item-id');
            const rating = parseInt(e.target.value);
            
            try {
                const rateRes = await fetch('/api/rate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, item_id, rating })
                });
                const rateData = await rateRes.json();
                
                // Update local memory ratings
                userRatings[username] = rateData.ratings;
                
                // Recalculate recommendations
                await loadUserRecommendations(username);
            } catch (e) {
                console.error(e);
            }
        });
        
        userRatingsList.appendChild(row);
    });
}

function renderCollabMath(explanation) {
    if (!explanation || !explanation.similarities) {
        collabMathPanel.style.display = 'none';
        return;
    }

    collabMathPanel.style.display = 'flex';
    peerSimilaritiesGrid.innerHTML = '';
    
    const sims = explanation.similarities;
    Object.keys(sims).forEach(peer => {
        const val = sims[peer];
        const valClass = val >= 0 ? 'positive' : 'negative';
        const sign = val >= 0 ? '+' : '';
        
        const card = document.createElement('div');
        card.className = 'peer-card';
        card.innerHTML = `
            <span class="peer-name">vs ${peer}</span>
            <span class="peer-sim-val ${valClass}">${sign}${val.toFixed(3)}</span>
        `;
        peerSimilaritiesGrid.appendChild(card);
    });
}

// Run initial loading
initializeDashboard();
