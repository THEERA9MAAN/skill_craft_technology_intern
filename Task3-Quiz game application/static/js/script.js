// ===================================
// PROFESSIONAL QUIZ APP - SCRIPT.JS
// ===================================

// Global Variables
let currentUser = null;
let subjects = [];
let currentSubject = null;
let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let correctAnswers = 0;

// ===================================
// INITIALIZATION
// ===================================
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});

// ===================================
// AUTHENTICATION
// ===================================
async function checkAuth() {
    try {
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            updateUIForLoggedInUser();
            loadSubjects();
        } else {
            updateUIForLoggedOutUser();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateUIForLoggedOutUser();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('login-btn').style.display = 'none';
    document.getElementById('register-btn').style.display = 'none';
    document.getElementById('user-menu').style.display = 'flex';
    document.getElementById('stats-btn').style.display = 'block';
    document.getElementById('user-name').textContent = currentUser.username;
}

function updateUIForLoggedOutUser() {
    document.getElementById('login-btn').style.display = 'block';
    document.getElementById('register-btn').style.display = 'block';
    document.getElementById('user-menu').style.display = 'none';
    document.getElementById('stats-btn').style.display = 'none';
}

async function register(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, email, password})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Registration successful! Please login.', 'success');
            showAuth('login');
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration failed. Please try again.', 'error');
    }
}

async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showToast('Login successful!', 'success');
            closeAuthModal();
            updateUIForLoggedInUser();
            loadSubjects();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}

async function logout() {
    try {
        await fetch('/api/logout', {method: 'POST'});
        currentUser = null;
        showToast('Logged out successfully', 'success');
        updateUIForLoggedOutUser();
        showHome();
    } catch (error) {
        showToast('Logout failed', 'error');
    }
}

// ===================================
// MODAL CONTROLS
// ===================================
function showAuth(type) {
    const modal = document.getElementById('auth-modal');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (type === 'login') {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    }
    
    modal.classList.add('active');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('active');
}

function closeLeaderboardModal() {
    document.getElementById('leaderboard-modal').classList.remove('active');
}

// ===================================
// NAVIGATION
// ===================================
function showHome() {
    document.getElementById('hero-section').style.display = 'block';
    document.getElementById('subjects-section').style.display = 'block';
    document.getElementById('quiz-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('stats-section').style.display = 'none';
    window.scrollTo(0, 0);
}

function scrollToSubjects() {
    document.getElementById('subjects-section').scrollIntoView({behavior: 'smooth'});
}

function backToSubjects() {
    showHome();
    if (currentUser) {
        loadSubjects();
    }
}

// ===================================
// SUBJECTS
// ===================================
async function loadSubjects() {
    try {
        const response = await fetch('/api/subjects');
        if (!response.ok) {
            showToast('Please login to view subjects', 'error');
            return;
        }
        
        subjects = await response.json();
        displaySubjects();
    } catch (error) {
        showToast('Failed to load subjects', 'error');
    }
}

function displaySubjects() {
    const grid = document.getElementById('subjects-grid');
    grid.innerHTML = '';
    
    subjects.forEach(subject => {
        const card = document.createElement('div');
        card.className = 'subject-card';
        card.onclick = () => startQuiz(subject);
        
        card.innerHTML = `
            <div class="subject-icon">${subject.icon}</div>
            <h3 class="subject-name">${subject.name}</h3>
            <p class="subject-description">${subject.description}</p>
        `;
        
        grid.appendChild(card);
    });
}

// ===================================
// QUIZ FUNCTIONALITY
// ===================================
async function startQuiz(subject) {
    currentSubject = subject;
    
    try {
        const response = await fetch(`/api/questions/${subject.id}`);
        questions = await response.json();
        
        if (questions.length === 0) {
            showToast('No questions available for this subject', 'error');
            return;
        }
        
        currentQuestionIndex = 0;
        score = 0;
        correctAnswers = 0;
        
        document.getElementById('hero-section').style.display = 'none';
        document.getElementById('subjects-section').style.display = 'none';
        document.getElementById('quiz-section').style.display = 'block';
        
        displayQuestion();
        updateProgress();
    } catch (error) {
        showToast('Failed to load questions', 'error');
    }
}

function displayQuestion() {
    const question = questions[currentQuestionIndex];
    
    document.getElementById('question-text').textContent = question.question_text;
    document.getElementById('question-counter').textContent = 
        `Question ${currentQuestionIndex + 1} of ${questions.length}`;
    document.getElementById('score-display').textContent = `Score: ${score}`;
    
    // Set difficulty badge
    const difficultyBadge = document.getElementById('difficulty-badge');
    difficultyBadge.textContent = question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1);
    difficultyBadge.className = `difficulty-badge ${question.difficulty}`;
    
    // Set question type badge
    const typeBadge = document.getElementById('question-type-badge');
    if (question.question_type === 'single') {
        typeBadge.textContent = '📝 Single Choice';
    } else if (question.question_type === 'multiple') {
        typeBadge.textContent = '☑️ Multiple Choice';
    } else if (question.question_type === 'fill') {
        typeBadge.textContent = '✍️ Fill in the Blank';
    }
    
    // Clear previous content
    document.getElementById('options-container').innerHTML = '';
    document.getElementById('fill-container').style.display = 'none';
    document.getElementById('feedback').style.display = 'none';
    document.getElementById('submit-btn').style.display = 'block';
    document.getElementById('next-btn').style.display = 'none';
    document.getElementById('submit-btn').disabled = false;
    
    // Display based on question type
    if (question.question_type === 'single') {
        displaySingleChoice(question);
    } else if (question.question_type === 'multiple') {
        displayMultipleChoice(question);
    } else if (question.question_type === 'fill') {
        displayFillInBlank();
    }
}

function displaySingleChoice(question) {
    const container = document.getElementById('options-container');
    
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.innerHTML = `
            <input type="radio" name="answer" id="option${index}" value="${option}">
            <label for="option${index}">${option}</label>
        `;
        
        optionDiv.onclick = function() {
            document.getElementById(`option${index}`).checked = true;
            document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
            optionDiv.classList.add('selected');
        };
        
        container.appendChild(optionDiv);
    });
}

function displayMultipleChoice(question) {
    const container = document.getElementById('options-container');
    
    question.options.forEach((option, index) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.innerHTML = `
            <input type="checkbox" name="answer" id="option${index}" value="${option}">
            <label for="option${index}">${option}</label>
        `;
        
        optionDiv.onclick = function(e) {
            if (e.target.tagName !== 'INPUT') {
                const checkbox = document.getElementById(`option${index}`);
                checkbox.checked = !checkbox.checked;
            }
            optionDiv.classList.toggle('selected');
        };
        
        container.appendChild(optionDiv);
    });
}

function displayFillInBlank() {
    const container = document.getElementById('fill-container');
    container.style.display = 'block';
    document.getElementById('fill-answer').value = '';
    document.getElementById('fill-answer').focus();
}

async function submitAnswer() {
    const question = questions[currentQuestionIndex];
    let userAnswer = '';
    
    // Get user answer based on question type
    if (question.question_type === 'single') {
        const selected = document.querySelector('input[name="answer"]:checked');
        if (!selected) {
            showToast('Please select an answer!', 'error');
            return;
        }
        userAnswer = selected.value;
    } else if (question.question_type === 'multiple') {
        const selected = document.querySelectorAll('input[name="answer"]:checked');
        if (selected.length === 0) {
            showToast('Please select at least one answer!', 'error');
            return;
        }
        userAnswer = Array.from(selected).map(input => input.value).join(',');
    } else if (question.question_type === 'fill') {
        userAnswer = document.getElementById('fill-answer').value.trim();
        if (!userAnswer) {
            showToast('Please enter an answer!', 'error');
            return;
        }
    }
    
    document.getElementById('submit-btn').disabled = true;
    
    try {
        const response = await fetch('/api/submit-answer', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                question_id: question.id,
                answer: userAnswer
            })
        });
        
        const result = await response.json();
        
        score += result.earned_points;
        if (result.correct) correctAnswers++;
        
        document.getElementById('score-display').textContent = `Score: ${score}`;
        
        showFeedback(result.correct, result.correct_answer, result.earned_points);
        
        document.getElementById('submit-btn').style.display = 'none';
        document.getElementById('next-btn').style.display = 'block';
        
        if (question.question_type === 'single' || question.question_type === 'multiple') {
            highlightAnswers(result.correct_answer, userAnswer);
        }
        
    } catch (error) {
        showToast('Failed to submit answer', 'error');
        document.getElementById('submit-btn').disabled = false;
    }
}

function highlightAnswers(correctAnswer, userAnswer) {
    const correctAnswers = correctAnswer.split(',').map(a => a.trim().toLowerCase());
    const userAnswersList = userAnswer.split(',').map(a => a.trim().toLowerCase());
    
    document.querySelectorAll('.option').forEach(option => {
        const input = option.querySelector('input');
        const value = input.value.toLowerCase();
        
        if (correctAnswers.includes(value)) {
            option.classList.add('correct');
        } else if (userAnswersList.includes(value)) {
            option.classList.add('incorrect');
        }
        
        input.disabled = true;
    });
}

function showFeedback(isCorrect, correctAnswer, points) {
    const feedback = document.getElementById('feedback');
    const feedbackText = document.getElementById('feedback-text');
    
    feedback.style.display = 'block';
    feedback.classList.remove('correct', 'incorrect');
    
    if (isCorrect) {
        feedback.classList.add('correct');
        feedbackText.innerHTML = `✓ Correct! You earned <strong>${points} points</strong>!`;
    } else {
        feedback.classList.add('incorrect');
        feedbackText.innerHTML = `✗ Incorrect. The correct answer is: <strong>${correctAnswer}</strong>`;
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    
    if (currentQuestionIndex < questions.length) {
        displayQuestion();
        updateProgress();
    } else {
        finishQuiz();
    }
}

function updateProgress() {
    const progress = ((currentQuestionIndex) / questions.length) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
}

async function finishQuiz() {
    try {
        const response = await fetch('/api/submit-quiz', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                subject_id: currentSubject.id,
                score: score,
                total_questions: questions.length
            })
        });
        
        const data = await response.json();
        
        document.getElementById('quiz-section').style.display = 'none';
        document.getElementById('results-section').style.display = 'flex';
        
        document.getElementById('final-score').textContent = score;
        document.getElementById('total-questions').textContent = questions.length;
        document.getElementById('correct-answers').textContent = correctAnswers;
        document.getElementById('final-percentage').textContent = data.percentage.toFixed(1) + '%';
        
    } catch (error) {
        showToast('Failed to save quiz results', 'error');
    }
}

// ===================================
// LEADERBOARD
// ===================================
async function showLeaderboard() {
    if (!currentSubject) {
        showToast('Please complete a quiz first', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/leaderboard/${currentSubject.id}`);
        const leaderboard = await response.json();
        
        const list = document.getElementById('leaderboard-list');
        list.innerHTML = '';
        
        if (leaderboard.length === 0) {
            list.innerHTML = '<p style="text-align: center; color: var(--gray);">No scores yet. Be the first!</p>';
        } else {
            leaderboard.forEach((entry, index) => {
                const item = document.createElement('div');
                item.className = 'leaderboard-item';
                
                const date = new Date(entry.completed_at);
                const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                
                item.innerHTML = `
                    <div class="leaderboard-rank">${index + 1}</div>
                    <div class="leaderboard-info">
                        <div class="leaderboard-username">${entry.username}</div>
                        <div class="leaderboard-date">${formattedDate}</div>
                    </div>
                    <div class="leaderboard-score">${entry.percentage}%</div>
                `;
                
                list.appendChild(item);
            });
        }
        
        document.getElementById('leaderboard-modal').classList.add('active');
        
    } catch (error) {
        showToast('Failed to load leaderboard', 'error');
    }
}

// ===================================
// USER STATISTICS
// ===================================
async function showStats() {
    try {
        const response = await fetch('/api/user-stats');
        const stats = await response.json();
        
        document.getElementById('hero-section').style.display = 'none';
        document.getElementById('subjects-section').style.display = 'none';
        document.getElementById('stats-section').style.display = 'block';
        
        const grid = document.getElementById('stats-grid');
        grid.innerHTML = '';
        
        stats.forEach(stat => {
            const card = document.createElement('div');
            card.className = 'stat-card';
            
            card.innerHTML = `
                <div class="stat-card-header">
                    <h3 class="stat-card-title">${stat.subject}</h3>
                    <span class="stat-card-icon">${stat.icon}</span>
                </div>
                <div class="stat-card-body">
                    <div class="stat-metric">
                        <div class="stat-metric-value">${stat.attempts}</div>
                        <div class="stat-metric-label">Attempts</div>
                    </div>
                    <div class="stat-metric">
                        <div class="stat-metric-value">${stat.best_score}%</div>
                        <div class="stat-metric-label">Best Score</div>
                    </div>
                    <div class="stat-metric">
                        <div class="stat-metric-value">${stat.avg_score}%</div>
                        <div class="stat-metric-label">Avg Score</div>
                    </div>
                </div>
            `;
            
            grid.appendChild(card);
        });
        
        window.scrollTo(0, 0);
        
    } catch (error) {
        showToast('Failed to load statistics', 'error');
    }
}

// ===================================
// TOAST NOTIFICATIONS
// ===================================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ===================================
// EVENT LISTENERS
// ===================================
// Close modals when clicking outside
window.onclick = function(event) {
    const authModal = document.getElementById('auth-modal');
    const leaderboardModal = document.getElementById('leaderboard-modal');
    
    if (event.target === authModal) {
        closeAuthModal();
    }
    if (event.target === leaderboardModal) {
        closeLeaderboardModal();
    }
}

// Allow Enter key for fill-in-the-blank
document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        const fillInput = document.getElementById('fill-answer');
        if (fillInput && fillInput.style.display !== 'none' && document.activeElement === fillInput) {
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn && submitBtn.style.display !== 'none') {
                submitAnswer();
            }
        }
    }
});