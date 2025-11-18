let tasks = [];
let currentView = 'today';
let editingTaskId = null;
let selectedPriority = 4;
let selectedDate = '';
let selectedTime = '';

// DOM Elements
const quickAddBtn = document.getElementById('quickAddBtn');
const quickTaskForm = document.getElementById('quickTaskForm');
const quickTaskInput = document.getElementById('quickTaskInput');
const quickTaskDesc = document.getElementById('quickTaskDesc');
const submitQuickBtn = document.getElementById('submitQuickBtn');
const cancelQuickBtn = document.getElementById('cancelQuickBtn');
const tasksContainer = document.getElementById('tasksContainer');
const emptyState = document.getElementById('emptyState');
const viewTitle = document.getElementById('viewTitle');
const viewSubtitle = document.getElementById('viewSubtitle');
const dueDateBtn = document.getElementById('dueDateBtn');
const priorityBtn = document.getElementById('priorityBtn');
const datePicker = document.getElementById('datePicker');
const priorityPicker = document.getElementById('priorityPicker');
const taskDate = document.getElementById('taskDate');
const taskTime = document.getElementById('taskTime');
const editModal = document.getElementById('editModal');
const closeModal = document.getElementById('closeModal');
const cancelEdit = document.getElementById('cancelEdit');
const saveEdit = document.getElementById('saveEdit');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    setupEventListeners();
    updateSubtitle();
});

function setupEventListeners() {
    // Quick add button
    quickAddBtn.addEventListener('click', showQuickForm);
    cancelQuickBtn.addEventListener('click', hideQuickForm);
    submitQuickBtn.addEventListener('click', handleAddTask);
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentView = e.currentTarget.dataset.view;
            updateView();
        });
    });
    
    // Date and Priority pickers
    dueDateBtn.addEventListener('click', () => {
        datePicker.style.display = datePicker.style.display === 'none' ? 'flex' : 'none';
        priorityPicker.style.display = 'none';
    });
    
    priorityBtn.addEventListener('click', () => {
        priorityPicker.style.display = priorityPicker.style.display === 'none' ? 'flex' : 'none';
        datePicker.style.display = 'none';
    });
    
    // Date selection
    taskDate.addEventListener('change', (e) => {
        selectedDate = e.target.value;
        updateDateButtonText();
    });
    
    taskTime.addEventListener('change', (e) => {
        selectedTime = e.target.value;
    });
    
    // Priority selection
    document.querySelectorAll('.priority-option').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.priority-option').forEach(b => b.classList.remove('selected'));
            e.currentTarget.classList.add('selected');
            selectedPriority = parseInt(e.currentTarget.dataset.priority);
        });
    });
    
    // Modal
    closeModal.addEventListener('click', hideEditModal);
    cancelEdit.addEventListener('click', hideEditModal);
    saveEdit.addEventListener('click', handleSaveEdit);
    
    // Close modal on outside click
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) hideEditModal();
    });
    
    // Enter key to submit
    quickTaskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleAddTask();
        }
    });
}

function showQuickForm() {
    quickTaskForm.style.display = 'block';
    quickTaskInput.focus();
}

function hideQuickForm() {
    quickTaskForm.style.display = 'none';
    quickTaskInput.value = '';
    quickTaskDesc.value = '';
    selectedDate = '';
    selectedTime = '';
    selectedPriority = 4;
    datePicker.style.display = 'none';
    priorityPicker.style.display = 'none';
    taskDate.value = '';
    taskTime.value = '';
    document.getElementById('dueDateText').textContent = 'Due date';
}

function updateDateButtonText() {
    const dateBtn = document.getElementById('dueDateText');
    if (selectedDate) {
        const date = new Date(selectedDate);
        dateBtn.textContent = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else {
        dateBtn.textContent = 'Due date';
    }
}

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        tasks = await response.json();
        updateView();
        updateCounts();
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

async function handleAddTask() {
    const title = quickTaskInput.value.trim();
    if (!title) return;
    
    const taskData = {
        title: title,
        description: quickTaskDesc.value.trim(),
        due_date: selectedDate,
        due_time: selectedTime,
        priority: selectedPriority,
        completed: 0
    };
    
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            await loadTasks();
            hideQuickForm();
        }
    } catch (error) {
        console.error('Error adding task:', error);
    }
}

function updateView() {
    let filteredTasks = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    switch(currentView) {
        case 'today':
            filteredTasks = tasks.filter(task => {
                if (!task.due_date) return false;
                const dueDate = new Date(task.due_date);
                dueDate.setHours(0, 0, 0, 0);
                return dueDate.getTime() === today.getTime();
            });
            viewTitle.textContent = 'Today';
            break;
        case 'upcoming':
            filteredTasks = tasks.filter(task => {
                if (!task.due_date) return false;
                const dueDate = new Date(task.due_date);
                dueDate.setHours(0, 0, 0, 0);
                return dueDate > today;
            });
            viewTitle.textContent = 'Upcoming';
            break;
        case 'all':
            filteredTasks = tasks;
            viewTitle.textContent = 'All Tasks';
            break;
    }
    
    renderTasks(filteredTasks);
}

function updateSubtitle() {
    const today = new Date();
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const dayName = days[today.getDay()];
    const month = months[today.getMonth()];
    const date = today.getDate();
    
    viewSubtitle.textContent = `${dayName} ${month} ${date}`;
}

function renderTasks(filteredTasks) {
    if (filteredTasks.length === 0) {
        tasksContainer.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    tasksContainer.style.display = 'flex';
    emptyState.style.display = 'none';
    
    // Sort by priority and completion
    filteredTasks.sort((a, b) => {
        if (a.completed !== b.completed) return a.completed - b.completed;
        return a.priority - b.priority;
    });
    
    tasksContainer.innerHTML = filteredTasks.map(task => createTaskHTML(task)).join('');
    attachTaskListeners();
}

function createTaskHTML(task) {
    const priorityColors = {
        1: '#d1453b',
        2: '#eb8909',
        3: '#246fe0',
        4: '#808080'
    };
    
    const completedClass = task.completed ? 'completed' : '';
    const priorityColor = priorityColors[task.priority || 4];
    
    let metaHTML = '';
    if (task.due_date) {
        const date = new Date(task.due_date);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        metaHTML += `<span><i class="fas fa-calendar"></i>${dateStr}</span>`;
    }
    if (task.due_time) {
        metaHTML += `<span><i class="fas fa-clock"></i>${task.due_time}</span>`;
    }
    
    return `
        <div class="task-item ${completedClass}" data-task-id="${task.id}">
            <div class="task-checkbox ${completedClass}" data-task-id="${task.id}"></div>
            <div class="task-content">
                <div class="task-title-row">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    ${task.priority && task.priority < 4 ? `<div class="task-priority"><i class="fas fa-flag" style="color: ${priorityColor};"></i></div>` : ''}
                </div>
                ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
                ${metaHTML ? `<div class="task-meta">${metaHTML}</div>` : ''}
            </div>
            <div class="task-actions">
                <button class="task-action-btn edit-task" data-task-id="${task.id}">
                    <i class="fas fa-pen"></i>
                </button>
                <button class="task-action-btn delete-task" data-task-id="${task.id}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
}

function attachTaskListeners() {
    // Checkbox listeners
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('click', (e) => {
            e.stopPropagation();
            const taskId = parseInt(checkbox.dataset.taskId);
            toggleTaskComplete(taskId);
        });
    });
    
    // Edit listeners
    document.querySelectorAll('.edit-task').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const taskId = parseInt(btn.dataset.taskId);
            showEditModal(taskId);
        });
    });
    
    // Delete listeners
    document.querySelectorAll('.delete-task').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const taskId = parseInt(btn.dataset.taskId);
            deleteTask(taskId);
        });
    });
}

async function toggleTaskComplete(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            await loadTasks();
        }
    } catch (error) {
        console.error('Error toggling task:', error);
    }
}

function showEditModal(taskId) {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    editingTaskId = taskId;
    document.getElementById('editTaskTitle').value = task.title;
    document.getElementById('editTaskDesc').value = task.description || '';
    document.getElementById('editTaskDate').value = task.due_date || '';
    document.getElementById('editTaskTime').value = task.due_time || '';
    
    editModal.classList.add('active');
}

function hideEditModal() {
    editModal.classList.remove('active');
    editingTaskId = null;
}

async function handleSaveEdit() {
    if (!editingTaskId) return;
    
    const taskData = {
        title: document.getElementById('editTaskTitle').value.trim(),
        description: document.getElementById('editTaskDesc').value.trim(),
        due_date: document.getElementById('editTaskDate').value,
        due_time: document.getElementById('editTaskTime').value
    };
    
    if (!taskData.title) {
        alert('Task title is required');
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${editingTaskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            await loadTasks();
            hideEditModal();
        }
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Delete this task?')) return;
    
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadTasks();
        }
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

function updateCounts() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Today count
    const todayCount = tasks.filter(task => {
        if (!task.due_date || task.completed) return false;
        const dueDate = new Date(task.due_date);
        dueDate.setHours(0, 0, 0, 0);
        return dueDate.getTime() === today.getTime();
    }).length;
    
    // Upcoming count
    const upcomingCount = tasks.filter(task => {
        if (!task.due_date || task.completed) return false;
        const dueDate = new Date(task.due_date);
        dueDate.setHours(0, 0, 0, 0);
        return dueDate > today;
    }).length;
    
    // All count
    const allCount = tasks.filter(task => !task.completed).length;
    
    document.getElementById('todayCount').textContent = todayCount;
    document.getElementById('upcomingCount').textContent = upcomingCount;
    document.getElementById('allCount').textContent = allCount;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}