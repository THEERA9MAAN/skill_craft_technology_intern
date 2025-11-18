from flask import Flask, render_template, request, jsonify # pyright: ignore[reportMissingImports]
import sqlite3
import os
import math
from datetime import datetime

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            mode TEXT DEFAULT 'basic',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversion_type TEXT NOT NULL,
            from_value REAL NOT NULL,
            from_unit TEXT NOT NULL,
            to_value REAL NOT NULL,
            to_unit TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data.get('expression', '')
        mode = data.get('mode', 'basic')
        angle_mode = data.get('angleMode', 'deg')
        
        # Input validation
        if not expression:
            return jsonify({'error': 'Empty expression'}), 400
        
        # Process the expression
        expr = expression
        
        # Replace mathematical symbols
        expr = expr.replace('π', str(math.pi))
        expr = expr.replace('×', '*')
        expr = expr.replace('÷', '/')
        expr = expr.replace('−', '-')
        
        # Handle percentage
        import re
        expr = re.sub(r'(\d+)%', r'(\1/100)', expr)
        
        # Handle square root
        expr = re.sub(r'√\(([^)]+)\)', r'math.sqrt(\1)', expr)
        
        # Handle square
        expr = re.sub(r'\(([^)]+)\)²', r'math.pow(\1,2)', expr)
        
        # Handle trigonometric functions
        if angle_mode == 'deg':
            expr = re.sub(r'sin\(([^)]+)\)', r'math.sin(math.radians(\1))', expr)
            expr = re.sub(r'cos\(([^)]+)\)', r'math.cos(math.radians(\1))', expr)
            expr = re.sub(r'tan\(([^)]+)\)', r'math.tan(math.radians(\1))', expr)
            expr = re.sub(r'asin\(([^)]+)\)', r'math.degrees(math.asin(\1))', expr)
            expr = re.sub(r'acos\(([^)]+)\)', r'math.degrees(math.acos(\1))', expr)
            expr = re.sub(r'atan\(([^)]+)\)', r'math.degrees(math.atan(\1))', expr)
        else:
            expr = re.sub(r'sin\(([^)]+)\)', r'math.sin(\1)', expr)
            expr = re.sub(r'cos\(([^)]+)\)', r'math.cos(\1)', expr)
            expr = re.sub(r'tan\(([^)]+)\)', r'math.tan(\1)', expr)
            expr = re.sub(r'asin\(([^)]+)\)', r'math.asin(\1)', expr)
            expr = re.sub(r'acos\(([^)]+)\)', r'math.acos(\1)', expr)
            expr = re.sub(r'atan\(([^)]+)\)', r'math.atan(\1)', expr)
        
        # Handle logarithms
        expr = re.sub(r'log\(([^)]+)\)', r'math.log10(\1)', expr)
        expr = re.sub(r'ln\(([^)]+)\)', r'math.log(\1)', expr)
        
        # Handle exponentials
        expr = re.sub(r'e\^\(([^)]+)\)', r'math.exp(\1)', expr)
        expr = re.sub(r'([0-9.]+)\^([0-9.]+)', r'math.pow(\1,\2)', expr)
        
        # Evaluate expression
        result = eval(expr, {"__builtins__": None}, {"math": math})
        
        # Handle invalid results
        if not math.isfinite(result):
            return jsonify({'error': 'Math error'}), 400
        
        # Format result
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 10)
        
        # Store in database
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        c.execute('INSERT INTO calculations (expression, result, mode) VALUES (?, ?, ?)',
                  (expression, str(result), mode))
        conn.commit()
        conn.close()
        
        return jsonify({'result': str(result)})
    
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero'}), 400
    except ValueError as e:
        return jsonify({'error': 'Math domain error'}), 400
    except SyntaxError:
        return jsonify({'error': 'Invalid syntax'}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid expression'}), 400

@app.route('/convert', methods=['POST'])
def convert_units():
    try:
        data = request.get_json()
        conversion_type = data.get('type', '')
        value = float(data.get('value', 0))
        from_unit = data.get('from_unit', '')
        to_unit = data.get('to_unit', '')
        
        # Conversion factors
        conversions = {
            'length': {
                'meter': 1,
                'kilometer': 0.001,
                'centimeter': 100,
                'millimeter': 1000,
                'mile': 0.000621371,
                'yard': 1.09361,
                'foot': 3.28084,
                'inch': 39.3701
            },
            'weight': {
                'kilogram': 1,
                'gram': 1000,
                'milligram': 1000000,
                'pound': 2.20462,
                'ounce': 35.274
            },
            'time': {
                'second': 1,
                'minute': 1/60,
                'hour': 1/3600,
                'day': 1/86400,
                'week': 1/604800
            }
        }
        
        # Temperature conversion
        if conversion_type == 'temperature':
            if from_unit == 'celsius':
                if to_unit == 'fahrenheit':
                    result = value * 9/5 + 32
                elif to_unit == 'kelvin':
                    result = value + 273.15
                else:
                    result = value
            elif from_unit == 'fahrenheit':
                if to_unit == 'celsius':
                    result = (value - 32) * 5/9
                elif to_unit == 'kelvin':
                    result = (value - 32) * 5/9 + 273.15
                else:
                    result = value
            elif from_unit == 'kelvin':
                if to_unit == 'celsius':
                    result = value - 273.15
                elif to_unit == 'fahrenheit':
                    result = (value - 273.15) * 9/5 + 32
                else:
                    result = value
            else:
                result = value
        else:
            # Standard unit conversion
            if conversion_type in conversions:
                units = conversions[conversion_type]
                base_value = value / units[from_unit]
                result = base_value * units[to_unit]
            else:
                result = value
        
        # Store in database
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        c.execute('''INSERT INTO conversions 
                     (conversion_type, from_value, from_unit, to_value, to_unit) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (conversion_type, value, from_unit, result, to_unit))
        conn.commit()
        conn.close()
        
        return jsonify({'result': round(result, 10)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 20, type=int)
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        c.execute('''SELECT expression, result, mode, timestamp 
                     FROM calculations 
                     ORDER BY id DESC 
                     LIMIT ?''', (limit,))
        history = c.fetchall()
        conn.close()
        
        return jsonify({
            'history': [
                {
                    'expression': h[0], 
                    'result': h[1], 
                    'mode': h[2],
                    'timestamp': h[3]
                }
                for h in history
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversion-history', methods=['GET'])
def get_conversion_history():
    try:
        limit = request.args.get('limit', 20, type=int)
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        c.execute('''SELECT conversion_type, from_value, from_unit, 
                            to_value, to_unit, timestamp 
                     FROM conversions 
                     ORDER BY id DESC 
                     LIMIT ?''', (limit,))
        history = c.fetchall()
        conn.close()
        
        return jsonify({
            'history': [
                {
                    'type': h[0],
                    'from_value': h[1],
                    'from_unit': h[2],
                    'to_value': h[3],
                    'to_unit': h[4],
                    'timestamp': h[5]
                }
                for h in history
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-history', methods=['POST'])
def clear_history():
    try:
        history_type = request.get_json().get('type', 'all')
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        
        if history_type == 'calculations':
            c.execute('DELETE FROM calculations')
        elif history_type == 'conversions':
            c.execute('DELETE FROM conversions')
        else:
            c.execute('DELETE FROM calculations')
            c.execute('DELETE FROM conversions')
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'History cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    try:
        conn = sqlite3.connect('calculator.db')
        c = conn.cursor()
        
        # Get calculation statistics
        c.execute('SELECT COUNT(*) FROM calculations')
        total_calculations = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM conversions')
        total_conversions = c.fetchone()[0]
        
        c.execute('''SELECT mode, COUNT(*) 
                     FROM calculations 
                     GROUP BY mode''')
        mode_stats = dict(c.fetchall())
        
        conn.close()
        
        return jsonify({
            'total_calculations': total_calculations,
            'total_conversions': total_conversions,
            'mode_statistics': mode_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)