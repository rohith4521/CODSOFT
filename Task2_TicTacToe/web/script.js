// ==========================================================================
// GAME STATE DEFINITION
// ==========================================================================
let board = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
let humanSymbol = 'X';
let aiSymbol = 'O';
let difficulty = 'unbeatable';
let starter = 'human';
let isGameOver = false;
let isAiThinking = false;

let scores = {
    human: 0,
    ai: 0,
    draws: 0
};

// Winning combinations map to coordinates on a 300x300 SVG viewbox
const WIN_COORDINATES = [
    // Rows
    { combo: [0, 1, 2], x1: 15, y1: 50, x2: 285, y2: 50 },
    { combo: [3, 4, 5], x1: 15, y1: 150, x2: 285, y2: 150 },
    { combo: [6, 7, 8], x1: 15, y1: 250, x2: 285, y2: 250 },
    // Columns
    { combo: [0, 3, 6], x1: 50, y1: 15, x2: 50, y2: 285 },
    { combo: [1, 4, 7], x1: 150, y1: 15, x2: 150, y2: 285 },
    { combo: [2, 5, 8], x1: 250, y1: 15, x2: 250, y2: 285 },
    // Diagonals
    { combo: [0, 4, 8], x1: 30, y1: 30, x2: 270, y2: 270 },
    { combo: [2, 4, 6], x1: 270, y1: 30, x2: 30, y2: 270 }
];

// ==========================================================================
// DOM ELEMENTS
// ==========================================================================
const gridCells = document.querySelectorAll('.grid-cell');
const gridContainer = document.getElementById('grid-container');
const winLineSvg = document.getElementById('winning-line-svg');
const winLine = document.getElementById('win-line');
const gameStatusHeading = document.getElementById('game-status-heading');
const gameStatusDesc = document.getElementById('game-status-desc');

// Score labels
const scoreHumanVal = document.getElementById('score-human-val');
const scoreAiVal = document.getElementById('score-ai-val');
const scoreDrawVal = document.getElementById('score-draw-val');

// Control Buttons
const difficultyButtons = document.querySelectorAll('#difficulty-control .segment');
const symbolButtons = document.querySelectorAll('#symbol-control .segment');
const starterButtons = document.querySelectorAll('#starter-control .segment');
const restartGameBtn = document.getElementById('restart-game');
const resetScoresBtn = document.getElementById('reset-scores');
const toastEl = document.getElementById('toast');

// ==========================================================================
// INITIALIZATION
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    resetBoard();
});

function setupEventListeners() {
    // Grid Cells click
    gridCells.forEach(cell => {
        cell.addEventListener('click', () => {
            const index = parseInt(cell.getAttribute('data-index'));
            handleCellClick(index);
        });
    });

    // Difficulty Settings Selector
    difficultyButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            difficultyButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            difficulty = btn.getAttribute('data-val');
            
            // Adjust body class for difficulty highlights
            document.body.className = `difficulty-${difficulty}`;
            showToast(`Difficulty set to: ${btn.innerText}`);
        });
    });

    // Symbol Settings Selector
    symbolButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            symbolButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            humanSymbol = btn.getAttribute('data-val');
            aiSymbol = humanSymbol === 'X' ? 'O' : 'X';
            
            showToast(`Your symbol: ${humanSymbol}`);
            resetBoard(); // Reset board to apply symbol changes
        });
    });

    // Starter Settings Selector
    starterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            starterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            starter = btn.getAttribute('data-val');
            
            showToast(`Starter: ${btn.innerText}`);
            resetBoard();
        });
    });

    // Restart Button
    restartGameBtn.addEventListener('click', () => {
        resetBoard();
        showToast('Game restarted');
    });

    // Reset Scores Button
    resetScoresBtn.addEventListener('click', () => {
        scores = { human: 0, ai: 0, draws: 0 };
        scoreHumanVal.innerText = '0';
        scoreAiVal.innerText = '0';
        scoreDrawVal.innerText = '0';
        showToast('Score statistics reset');
    });
}

// ==========================================================================
// GAMEPLAY LOGIC & REST CONNECTIVITY
// ==========================================================================

function handleCellClick(index) {
    // Validation checks
    if (board[index] !== ' ' || isGameOver || isAiThinking) {
        return;
    }

    // 1. Human makes a move
    makeMove(index, humanSymbol);

    // 2. Check game status
    const winner = checkWinnerLocal(board);
    if (winner) {
        endGame(winner);
        return;
    }

    // 3. Switch turn to AI
    isAiThinking = true;
    gridContainer.classList.add('disabled');
    gameStatusHeading.innerText = 'AI Turn';
    gameStatusDesc.innerText = 'AI is calculating next move...';

    // 4. Fetch AI move from server
    fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            board: board,
            ai_symbol: aiSymbol,
            difficulty: difficulty
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('API server returned error');
        }
        return response.json();
    })
    .then(data => {
        // AI response received
        isAiThinking = false;
        gridContainer.classList.remove('disabled');

        if (data.move !== -1) {
            makeMove(data.move, aiSymbol);
        }

        if (data.winner) {
            endGame(data.winner);
        } else {
            gameStatusHeading.innerText = 'Your Turn';
            gameStatusDesc.innerText = `Place your '${humanSymbol}' on an empty square.`;
        }
    })
    .catch(error => {
        console.error('Error fetching AI move:', error);
        isAiThinking = false;
        gridContainer.classList.remove('disabled');
        gameStatusHeading.innerText = 'Connection Offline';
        gameStatusDesc.innerText = 'Failed to fetch AI move from server.';
    });
}

function makeMove(index, symbol) {
    board[index] = symbol;
    const cell = document.querySelector(`.grid-cell[data-index="${index}"]`);
    cell.innerText = symbol;
    cell.classList.add(symbol === 'X' ? 'cell-x' : 'cell-o');
}

function resetBoard() {
    board = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '];
    isGameOver = false;
    isAiThinking = false;
    
    // Reset GUI grid cells
    gridCells.forEach(cell => {
        cell.innerText = '';
        cell.className = 'grid-cell';
    });
    gridContainer.classList.remove('disabled');

    // Reset winning line
    winLineSvg.className = 'winning-line-svg';
    winLine.setAttribute('x1', '0');
    winLine.setAttribute('y1', '0');
    winLine.setAttribute('x2', '0');
    winLine.setAttribute('y2', '0');

    // Set starter status
    if (starter === 'ai') {
        isAiThinking = true;
        gridContainer.classList.add('disabled');
        gameStatusHeading.innerText = 'AI Turn';
        gameStatusDesc.innerText = 'AI is playing first...';
        
        // Trigger initial AI move call after a short delay
        setTimeout(triggerFirstAiMove, 600);
    } else {
        gameStatusHeading.innerText = 'Your Turn';
        gameStatusDesc.innerText = `Select a square. You are playing as '${humanSymbol}'.`;
    }
}

function triggerFirstAiMove() {
    fetch('/api/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            board: board,
            ai_symbol: aiSymbol,
            difficulty: difficulty
        })
    })
    .then(response => response.json())
    .then(data => {
        isAiThinking = false;
        gridContainer.classList.remove('disabled');
        
        if (data.move !== -1) {
            makeMove(data.move, aiSymbol);
        }
        
        gameStatusHeading.innerText = 'Your Turn';
        gameStatusDesc.innerText = `AI has placed '${aiSymbol}'. Your turn to make a move.`;
    })
    .catch(error => {
        isAiThinking = false;
        gridContainer.classList.remove('disabled');
        gameStatusHeading.innerText = 'Offline';
        gameStatusDesc.innerText = 'Failed to query first move.';
    });
}

// ==========================================================================
// WIN CONDITION EVALUATORS & RENDERERS
// ==========================================================================

function checkWinnerLocal(b) {
    const wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
        [0, 4, 8], [2, 4, 6]             // diagonals
    ];
    for (let combo of wins) {
        if (b[combo[0]] !== ' ' && b[combo[0]] === b[combo[1]] && b[combo[0]] === b[combo[2]]) {
            return b[combo[0]];
        }
    }
    if (!b.includes(' ')) {
        return 'Tie';
    }
    return null;
}

function endGame(winner) {
    isGameOver = true;
    gridContainer.classList.add('disabled');

    if (winner === 'Tie') {
        scores.draws++;
        scoreDrawVal.innerText = scores.draws;
        gameStatusHeading.innerText = 'Draw!';
        gameStatusDesc.innerText = 'The board is full. Excellent defense!';
        winLineSvg.className = 'winning-line-svg win-draw';
    } else if (winner === humanSymbol) {
        scores.human++;
        scoreHumanVal.innerText = scores.human;
        gameStatusHeading.innerText = 'Victory!';
        gameStatusDesc.innerText = 'You defeated the AI agent!';
        
        // Find winning line coordinates
        drawWinLine(winner);
    } else {
        scores.ai++;
        scoreAiVal.innerText = scores.ai;
        gameStatusHeading.innerText = 'Defeat!';
        gameStatusDesc.innerText = 'The AI agent won this round.';
        
        // Find winning line coordinates
        drawWinLine(winner);
    }
}

function drawWinLine(winner) {
    // Check which combo won
    let winningCombo = null;
    for (let combo of [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]) {
        if (board[combo[0]] !== ' ' && board[combo[0]] === board[combo[1]] && board[combo[0]] === board[combo[2]]) {
            winningCombo = combo;
            break;
        }
    }

    if (!winningCombo) return;

    // Match combo with coordinate points
    const coords = WIN_COORDINATES.find(c => 
        c.combo[0] === winningCombo[0] && 
        c.combo[1] === winningCombo[1] && 
        c.combo[2] === winningCombo[2]
    );

    if (coords) {
        winLine.setAttribute('x1', coords.x1.toString());
        winLine.setAttribute('y1', coords.y1.toString());
        winLine.setAttribute('x2', coords.x2.toString());
        winLine.setAttribute('y2', coords.y2.toString());
        
        winLineSvg.className = `winning-line-svg win-${winner.toLowerCase()}`;
    }
}

function showToast(message) {
    toastEl.innerText = message;
    toastEl.classList.add('show');
    setTimeout(() => {
        toastEl.classList.remove('show');
    }, 2000);
}
