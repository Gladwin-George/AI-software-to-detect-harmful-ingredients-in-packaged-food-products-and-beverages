import cv2
import easyocr
import numpy as np
import os
import sqlite3
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import Flask, render_template, request, redirect, url_for, session, jsonify


app = Flask(__name__)
app.secret_key = 'your secret key'  # Set the secret key for your Flask application to use sessions

# Create SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,        
        password TEXT NOT NULL,
        obese TEXT NOT NULL,
        diabetes TEXT NOT NULL,
        high_bp TEXT NOT NULL,
        high_cholesterol TEXT NOT NULL,
        fatty_liver TEXT NOT NULL,
        kidney TEXT NOT NULL,
        heart_problem TEXT NOT NULL,
        lactose_intolerance TEXT NOT NULL
    )
''')
conn.commit()
conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    harmful_ingredients = []

    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            error = "No file uploaded"

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            error = "No selected file"

        # If the file exists and is allowed, proceed with OCR and detection
        if file and not error:
            filename = 'uploaded_image.jpg'
            file.save(filename)

            # Step 1: Extract text from the image
            img = cv2.imread(filename)
            reader = easyocr.Reader(['en'])
            text_results = reader.readtext(filename)
            extracted_text = ' '.join([result[1] for result in text_results])
            print(f'Extracted text: {extracted_text}')

            # Step 2: Load harmful ingredients from SQLite database into a dictionary
            harmful_ingredients_dict = {}
            conn = sqlite3.connect('harmful_ingredients.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM harmful_ingredients")
            for row in cursor.fetchall():
                        ingredient_name = row[1].strip()  # Assuming ingredient name is in the first column
                        harmful_ingredient_description = row[2].strip()  # Assuming harmful ingredient description is in the second column
                        harmful_ingredients_dict[ingredient_name.lower()] = harmful_ingredient_description
            conn.close()

            # Step 3: Identify harmful ingredients
            for ingredient_name, description in harmful_ingredients_dict.items():
                if ingredient_name in extracted_text.lower():
                    harmful_ingredients.append((ingredient_name, description))
                    print(f'Found harmful ingredient: {ingredient_name} - {description}')

            os.remove(filename)  # Remove the uploaded image

        return jsonify({'error': error, 'harmful_ingredients': harmful_ingredients})

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        gender = request.form['gender']
        password = request.form['password']
        obese = request.form['obese']
        diabetes = request.form['diabetes']
        high_bp = request.form['high_bp']
        high_cholesterol = request.form['high_cholesterol']
        fatty_liver = request.form['fatty_liver']
        kidney = request.form['kidney']
        heart_problem = request.form['heart_problem']
        lactose_intolerance = request.form['lactose_intolerance']

        # Check if the email is already registered
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Email is already registered'
        else:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert the user into the database with additional information
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, age, gender, password, obese, diabetes, high_bp, high_cholesterol, fatty_liver, kidney, heart_problem, lactose_intolerance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (name, email, age, gender, hashed_password, obese, diabetes, high_bp, high_cholesterol, fatty_liver, kidney, heart_problem, lactose_intolerance))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Retrieve the user by email
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Check password hash
            if bcrypt.checkpw(password.encode('utf-8'), user[5]):
                session['user_id'] = user[0]  # Store user ID in session
                return redirect(url_for('index'))

        # Invalid credentials or user does not exist
        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
