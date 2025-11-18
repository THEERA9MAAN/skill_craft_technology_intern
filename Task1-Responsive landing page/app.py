from flask import Flask, render_template, request, jsonify, redirect, url_for # pyright: ignore[reportMissingImports]
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database setup
DATABASE = 'website.db'

def get_db():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS newsletter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        db.close()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@app.route('/services')
def services():
    """Services page route"""
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page route with form handling"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if name and email and message:
            db = get_db()
            db.execute(
                'INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)',
                (name, email, message)
            )
            db.commit()
            db.close()
            return jsonify({'success': True, 'message': 'Message sent successfully!'})
        return jsonify({'success': False, 'message': 'All fields are required!'})
    
    return render_template('contact.html')

@app.route('/api/newsletter', methods=['POST'])
def newsletter():
    """Newsletter subscription endpoint"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required!'})
    
    try:
        db = get_db()
        db.execute('INSERT INTO newsletter (email) VALUES (?)', (email,))
        db.commit()
        db.close()
        return jsonify({'success': True, 'message': 'Subscribed successfully!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already subscribed!'})

@app.route('/admin/contacts')
def admin_contacts():
    """View all contact form submissions"""
    db = get_db()
    contacts = db.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin_contacts.html', contacts=contacts)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)