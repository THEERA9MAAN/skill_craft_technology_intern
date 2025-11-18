from flask import Flask, render_template, request, jsonify # pyright: ignore[reportMissingImports]
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'todoist.db'

def get_db():
    """Create a database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tasks table"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                due_time TEXT,
                priority INTEGER DEFAULT 4,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        db.close()

# Routes
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks ordered by priority and due date"""
    db = get_db()
    tasks = db.execute(
        'SELECT * FROM tasks ORDER BY completed ASC, priority ASC, due_date ASC'
    ).fetchall()
    db.close()
    
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'due_date': task['due_date'],
            'due_time': task['due_time'],
            'priority': task['priority'],
            'completed': task['completed'],
            'created_at': task['created_at']
        })
    
    return jsonify(tasks_list)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a new task"""
    data = request.json
    db = get_db()
    
    cursor = db.execute(
        'INSERT INTO tasks (title, description, due_date, due_time, priority) VALUES (?, ?, ?, ?, ?)',
        (
            data.get('title'),
            data.get('description'),
            data.get('due_date'),
            data.get('due_time'),
            data.get('priority', 4)
        )
    )
    db.commit()
    
    task_id = cursor.lastrowid
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    db.close()
    
    return jsonify({
        'id': task['id'],
        'title': task['title'],
        'description': task['description'],
        'due_date': task['due_date'],
        'due_time': task['due_time'],
        'priority': task['priority'],
        'completed': task['completed'],
        'created_at': task['created_at']
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    data = request.json
    db = get_db()
    
    db.execute(
        'UPDATE tasks SET title = ?, description = ?, due_date = ?, due_time = ? WHERE id = ?',
        (
            data.get('title'),
            data.get('description'),
            data.get('due_date'),
            data.get('due_time'),
            task_id
        )
    )
    db.commit()
    
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    db.close()
    
    if task:
        return jsonify({
            'id': task['id'],
            'title': task['title'],
            'description': task['description'],
            'due_date': task['due_date'],
            'due_time': task['due_time'],
            'priority': task['priority'],
            'completed': task['completed'],
            'created_at': task['created_at']
        })
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>/toggle', methods=['PUT'])
def toggle_task(task_id):
    """Toggle task completion status"""
    db = get_db()
    
    task = db.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task:
        new_status = 0 if task['completed'] else 1
        db.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        db.commit()
        db.close()
        return jsonify({'completed': new_status})
    
    db.close()
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    db.close()
    
    return jsonify({'message': 'Task deleted'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)