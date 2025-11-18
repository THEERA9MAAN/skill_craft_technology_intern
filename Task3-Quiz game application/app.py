from flask import Flask, render_template, request, jsonify, session  # pyright: ignore[reportMissingImports]
from flask_sqlalchemy import SQLAlchemy  # pyright: ignore[reportMissingImports]
from flask_cors import CORS  # pyright: ignore[reportMissingModuleSource]
from werkzeug.security import generate_password_hash, check_password_hash  # pyright: ignore[reportMissingImports]
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codequiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    questions = db.relationship('Question', backref='subject', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)  # 0=A, 1=B, 2=C, 3=D
    difficulty = db.Column(db.String(20), nullable=False)  # Easy, Medium, Hard
    explanation = db.Column(db.Text)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    subject = db.relationship('Subject', backref='attempts')

# ==================== INITIALIZE DATABASE ====================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Subject.query.first():
            return
        
        # Add subjects
        subjects_data = [
            {'name': 'Python', 'icon': '🐍', 'description': 'Master Python fundamentals'},
            {'name': 'JavaScript', 'icon': '⚡', 'description': 'Learn modern JavaScript'},
            {'name': 'Java', 'icon': '☕', 'description': 'Core Java concepts'},
            {'name': 'C++', 'icon': '⚙️', 'description': 'Object-oriented programming'},
            {'name': 'React', 'icon': '⚛️', 'description': 'Build modern UIs'},
            {'name': 'Node.js', 'icon': '🟢', 'description': 'Backend development'},
            {'name': 'SQL', 'icon': '🗄️', 'description': 'Database querying'},
            {'name': 'HTML/CSS', 'icon': '🎨', 'description': 'Web design basics'},
            {'name': 'Git', 'icon': '📦', 'description': 'Version control'},
            {'name': 'Docker', 'icon': '🐳', 'description': 'Containerization'},
            {'name': 'TypeScript', 'icon': '📘', 'description': 'Typed JavaScript'},
            {'name': 'MongoDB', 'icon': '🍃', 'description': 'NoSQL database'}
        ]
        
        for subj in subjects_data:
            subject = Subject(**subj)
            db.session.add(subject)
        
        db.session.commit()
        
        # -------------------- Sample Questions --------------------
        sample_questions = {
            'Python': [
                {'question_text': 'What is Python?', 'option_a':'Compiled','option_b':'Interpreted','option_c':'OS','option_d':'DB','correct_answer':1,'difficulty':'Easy','explanation':'Python is interpreted'},
                {'question_text':'Python file extension?', 'option_a':'.pt', 'option_b':'.pyt','option_c':'.py','option_d':'.python','correct_answer':2,'difficulty':'Easy','explanation':'Python files use .py'},
                {'question_text':'Comment in Python?', 'option_a':'//','option_b':'#','option_c':'/* */','option_d':'--','correct_answer':1,'difficulty':'Easy','explanation':'Use #'},
                {'question_text':'Output function in Python?', 'option_a':'echo()','option_b':'print()','option_c':'display()','option_d':'show()','correct_answer':1,'difficulty':'Easy','explanation':'Use print()'},
                {'question_text':'Variable assignment?', 'option_a':'x=5','option_b':'int x=5','option_c':'var x=5','option_d':'declare x=5','correct_answer':0,'difficulty':'Easy','explanation':'x=5 creates variable'},
                {'question_text':'Invalid variable name?', 'option_a':'my_var','option_b':'_myvar','option_c':'2myvar','option_d':'myVar2','correct_answer':2,'difficulty':'Easy','explanation':'Cannot start with number'},
                {'question_text':'Output of print(10+5)?','option_a':'105','option_b':'15','option_c':'10+5','option_d':'Error','correct_answer':1,'difficulty':'Easy','explanation':'Addition gives 15'},
                {'question_text':'Keyword for function?','option_a':'def','option_b':'function','option_c':'func','option_d':'define','correct_answer':0,'difficulty':'Easy','explanation':'def defines function'},
                {'question_text':'Length of object?','option_a':'len()','option_b':'length()','option_c':'size()','option_d':'count()','correct_answer':0,'difficulty':'Easy','explanation':'len() returns length'},
                {'question_text':'Get input from user?','option_a':'input()','option_b':'get()','option_c':'read()','option_d':'scan()','correct_answer':0,'difficulty':'Easy','explanation':'Use input()'}
            ],
            'JavaScript': [
                {'question_text':'What is JavaScript?','option_a':'Compiled','option_b':'Scripting','option_c':'DB','option_d':'Markup','correct_answer':1,'difficulty':'Easy','explanation':'JS is scripting language'},
                {'question_text':'Include JS in HTML?','option_a':'<js>','option_b':'<script>','option_c':'<javascript>','option_d':'<code>','correct_answer':1,'difficulty':'Easy','explanation':'Use <script>'},
                {'question_text':'Single-line comment in JS?','option_a':'//','option_b':'#','option_c':'<!-- -->','option_d':'/* */','correct_answer':0,'difficulty':'Easy','explanation':'Use //'},
                {'question_text':'Output to console?','option_a':'log.console()','option_b':'console.log()','option_c':'print()','option_d':'console.show()','correct_answer':1,'difficulty':'Easy','explanation':'console.log() prints'},
                {'question_text':'Declare variable in JS?','option_a':'var','option_b':'let','option_c':'const','option_d':'All','correct_answer':3,'difficulty':'Easy','explanation':'Supports var, let, const'},
                {'question_text':'10+"5" output?','option_a':'15','option_b':'105','option_c':'Error','option_d':'undefined','correct_answer':1,'difficulty':'Easy','explanation':'Concatenates to "105"'},
                {'question_text':'Strict equality?','option_a':'==','option_b':'===','option_c':'=','option_d':'equal','correct_answer':1,'difficulty':'Easy','explanation':'=== checks value and type'},
                {'question_text':'If statement syntax?','option_a':'if x=5','option_b':'if(x==5)','option_c':'if x==5:','option_d':'if x=5:','correct_answer':1,'difficulty':'Easy','explanation':'Use if(condition)'},
                {'question_text':'Create function in JS?','option_a':'function myFunc(){}','option_b':'def myFunc():','option_c':'create myFunc()','option_d':'func myFunc()','correct_answer':0,'difficulty':'Easy','explanation':'function name(){}'},
                {'question_text':'JS typing?','option_a':'Static','option_b':'Dynamic','option_c':'Strong','option_d':'None','correct_answer':1,'difficulty':'Medium','explanation':'JS is dynamically typed'}
            ],
            'Java': [
                {'question_text':'Java is...','option_a':'Compiled','option_b':'Interpreted','option_c':'Both','option_d':'None','correct_answer':2,'difficulty':'Easy','explanation':'Both compiled and interpreted'},
                {'question_text':'Entry point method?','option_a':'main()','option_b':'start()','option_c':'init()','option_d':'run()','correct_answer':0,'difficulty':'Easy','explanation':'main() is entry point'},
                {'question_text':'Class keyword?','option_a':'class','option_b':'def','option_c':'function','option_d':'struct','correct_answer':0,'difficulty':'Easy','explanation':'class defines a class'},
                {'question_text':'Java comments?','option_a':'//','option_b':'#','option_c':'<!-- -->','option_d':'**','correct_answer':0,'difficulty':'Easy','explanation':'Use //'},
                {'question_text':'Create object?','option_a':'new Class()','option_b':'Class()','option_c':'object Class','option_d':'make Class','correct_answer':0,'difficulty':'Easy','explanation':'Use new keyword'},
                {'question_text':'Package keyword?','option_a':'package','option_b':'import','option_c':'namespace','option_d':'using','correct_answer':0,'difficulty':'Easy','explanation':'package declares package'},
                {'question_text':'Java main args type?','option_a':'String[]','option_b':'string','option_c':'Array','option_d':'List','correct_answer':0,'difficulty':'Easy','explanation':'String array'},
                {'question_text':'Loop syntax?','option_a':'for(i=0;i<n;i++)','option_b':'while(i<n)','option_c':'do{}while','option_d':'All','correct_answer':3,'difficulty':'Easy','explanation':'All are valid loops'},
                {'question_text':'Inheritance keyword?','option_a':'extends','option_b':'implements','option_c':'inherits','option_d':'parent','correct_answer':0,'difficulty':'Easy','explanation':'Use extends'},
                {'question_text':'Access modifier private?','option_a':'public','option_b':'private','option_c':'protected','option_d':'internal','correct_answer':1,'difficulty':'Easy','explanation':'Use private'}
            ],
            'C++': [
                {'question_text':'C++ is...', 'option_a':'Procedural','option_b':'OOP','option_c':'Both','option_d':'None','correct_answer':2,'difficulty':'Easy','explanation':'C++ supports both'},
                {'question_text':'Include header file?', 'option_a':'#include','option_b':'import','option_c':'using','option_d':'include','correct_answer':0,'difficulty':'Easy','explanation':'Use #include'},
                {'question_text':'C++ main return type?', 'option_a':'void','option_b':'int','option_c':'float','option_d':'string','correct_answer':1,'difficulty':'Easy','explanation':'int main() returns int'},
                {'question_text':'Comment in C++?', 'option_a':'//','option_b':'#','option_c':'/* */','option_d':'Both A & C','correct_answer':3,'difficulty':'Easy','explanation':'Both valid'},
                {'question_text':'Declare variable?', 'option_a':'int x=5;','option_b':'x int=5;','option_c':'var x=5;','option_d':'let x=5;','correct_answer':0,'difficulty':'Easy','explanation':'Use type variable'},
                {'question_text':'Loop syntax?', 'option_a':'for','option_b':'while','option_c':'do-while','option_d':'All','correct_answer':3,'difficulty':'Easy','explanation':'All are valid'},
                {'question_text':'Access modifier public?','option_a':'public','option_b':'private','option_c':'protected','option_d':'internal','correct_answer':0,'difficulty':'Easy','explanation':'Use public'},
                {'question_text':'C++ function keyword?', 'option_a':'def','option_b':'func','option_c':'return_type name()','option_d':'function','correct_answer':2,'difficulty':'Easy','explanation':'Return type followed by name'},
                {'question_text':'Create object?', 'option_a':'Class obj;','option_b':'new Class();','option_c':'object Class','option_d':'make Class','correct_answer':0,'difficulty':'Easy','explanation':'Class obj; creates object'},
                {'question_text':'Pointer symbol?', 'option_a':'*','option_b':'&','option_c':'%','option_d':'#','correct_answer':0,'difficulty':'Easy','explanation':'Use *'}
            ],
            'React': [{'question_text':'React is...','option_a':'Library','option_b':'Framework','option_c':'Language','option_d':'DB','correct_answer':0,'difficulty':'Easy','explanation':'React is a library'}]*10,
            'Node.js':[{'question_text':'Node.js is...','option_a':'Backend JS','option_b':'Frontend JS','option_c':'Database','option_d':'OS','correct_answer':0,'difficulty':'Easy','explanation':'Backend JS'}]*10,
            'SQL':[{'question_text':'SQL is...','option_a':'Database Language','option_b':'Programming','option_c':'Markup','option_d':'Scripting','correct_answer':0,'difficulty':'Easy','explanation':'SQL used for DB'}]*10,
            'HTML/CSS':[{'question_text':'HTML tag for paragraph?','option_a':'<p>','option_b':'<h1>','option_c':'<div>','option_d':'<span>','correct_answer':0,'difficulty':'Easy','explanation':'<p> tag used'}]*10,
            'Git':[{'question_text':'Command to commit?','option_a':'git commit','option_b':'git push','option_c':'git pull','option_d':'git add','correct_answer':0,'difficulty':'Easy','explanation':'git commit commits'}]*10,
            'Docker':[{'question_text':'Docker container run?','option_a':'docker run','option_b':'docker start','option_c':'docker build','option_d':'docker exec','correct_answer':0,'difficulty':'Easy','explanation':'docker run starts container'}]*10,
            'TypeScript':[{'question_text':'TypeScript adds...?','option_a':'Types','option_b':'UI','option_c':'DB','option_d':'Backend','correct_answer':0,'difficulty':'Easy','explanation':'TypeScript adds types'}]*10,
            'MongoDB':[{'question_text':'MongoDB is...?','option_a':'NoSQL DB','option_b':'SQL DB','option_c':'OS','option_d':'Library','correct_answer':0,'difficulty':'Easy','explanation':'MongoDB is NoSQL'}]*10
        }
        
        for subject_name, questions in sample_questions.items():
            subj = Subject.query.filter_by(name=subject_name).first()
            for q in questions:
                question = Question(subject_id=subj.id, **q)
                db.session.add(question)
        
        db.session.commit()
        print("Database initialized with sample subjects and questions.")


# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all subjects with question count"""
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'icon': s.icon,
        'description': s.description,
        'question_count': len(s.questions)
    } for s in subjects])

@app.route('/api/questions/<int:subject_id>', methods=['GET'])
def get_questions(subject_id):
    """Get all questions for a subject"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    questions = Question.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': q.id,
        'question': q.question_text,
        'options': [q.option_a, q.option_b, q.option_c, q.option_d],
        'correct': q.correct_answer,
        'difficulty': q.difficulty,
        'explanation': q.explanation
    } for q in questions])

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password
    )
    
    db.session.add(user)
    db.session.commit()
    
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'message': 'Registration successful',
        'user': {'id': user.id, 'username': user.username, 'email': user.email}
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({
            'authenticated': True,
            'user': {'id': user.id, 'username': user.username, 'email': user.email}
        })
    return jsonify({'authenticated': False})

@app.route('/api/submit-quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz attempt and save score"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.json
    attempt = QuizAttempt(
        user_id=session['user_id'],
        subject_id=data['subject_id'],
        score=data['score'],
        total_questions=data['total_questions']
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({'message': 'Quiz submitted successfully'})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top scores across all users"""
    results = db.session.query(
        User.username,
        Subject.name.label('subject'),
        QuizAttempt.score,
        QuizAttempt.total_questions,
        QuizAttempt.completed_at
    ).join(QuizAttempt).join(Subject).order_by(
        QuizAttempt.score.desc()
    ).limit(10).all()
    
    return jsonify([{
        'username': r.username,
        'subject': r.subject,
        'score': r.score,
        'total': r.total_questions,
        'percentage': round((r.score / (r.total_questions * 10)) * 100),
        'date': r.completed_at.strftime('%Y-%m-%d')
    } for r in results])

@app.route('/api/user-stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    attempts = QuizAttempt.query.filter_by(user_id=session['user_id']).all()
    
    if not attempts:
        return jsonify({
            'total_quizzes': 0,
            'average_score': 0,
            'total_score': 0,
            'subjects_attempted': []
        })
    
    total_score = sum(a.score for a in attempts)
    avg_score = total_score / len(attempts)
    
    subject_stats = {}
    for attempt in attempts:
        subj_name = attempt.subject.name
        if subj_name not in subject_stats:
            subject_stats[subj_name] = {'count': 0, 'total': 0}
        subject_stats[subj_name]['count'] += 1
        subject_stats[subj_name]['total'] += attempt.score
    
    return jsonify({
        'total_quizzes': len(attempts),
        'average_score': round(avg_score, 2),
        'total_score': total_score,
        'subjects_attempted': [{
            'subject': k,
            'attempts': v['count'],
            'average': round(v['total'] / v['count'], 2)
        } for k, v in subject_stats.items()]
    })

# ==================== RUN APP ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)