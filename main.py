import os
import cv2
import easyocr
import numpy as np
import sqlite3
import bcrypt
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
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
        kidney_problem TEXT NOT NULL,
        heart_problem TEXT NOT NULL,
        lactose_intolerance TEXT NOT NULL,
        family_doctor_name TEXT,
        family_doctor_email TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS harmful_ingredients_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ingredient_name TEXT NOT NULL,
        description TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

conn.commit()
conn.close()


email = os.getenv('EMAIL')
password = os.getenv('EMAIL_PASSWORD')

#
def analyze_general_harmful_ingredients(file):
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
    harmful_ingredients = []
    for ingredient_name, description in harmful_ingredients_dict.items():
        if ingredient_name in extracted_text.lower():
            harmful_ingredients.append((ingredient_name, description))
            print(f'Found harmful ingredient: {ingredient_name} - {description}')

    os.remove(filename)  # Remove the uploaded image

    return harmful_ingredients


def get_harmful_ingredients(user_profile):
    conn = sqlite3.connect('harmful_ingredients.db')
    cursor = conn.cursor()
    query = '''
        SELECT name
        FROM harmful_ingredients
        WHERE (
            (age_min <= ? OR age_min IS NULL) AND
            (age_max >= ? OR age_max IS NULL) AND
            (gender = ? OR gender = 'both') AND
            ((obese = 'yes' AND ? = 'yes') OR 
            (diabetes = 'yes' AND ? = 'yes') OR 
            (high_bp = 'yes' AND ? = 'yes') OR 
            (high_cholesterol = 'yes' AND ? = 'yes') OR 
            (fatty_liver = 'yes' AND ? = 'yes') OR 
            (kidney_problem = 'yes' AND ? = 'yes') OR 
            (heart_problem = 'yes' AND ? = 'yes') OR 
            (lactose_intolerance = 'yes' AND ? = 'yes'))
        )
    '''
    cursor.execute(query, (user_profile[3], user_profile[3], user_profile[4], user_profile[6], user_profile[7], user_profile[8], user_profile[9], user_profile[10], user_profile[11], user_profile[12], user_profile[13]))
    return cursor.fetchall()

def analyze_harmful_ingredients(file, user_profile):
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
    harmful_ingredients = []
    extracted_text_words = set(extracted_text.lower().split())
    for ingredient_name, description in harmful_ingredients_dict.items():
        ingredient_name_words = ingredient_name.split()
        if any(word in extracted_text_words for word in ingredient_name_words):
            harmful_ingredients.append((ingredient_name, description))
            print(f'Found harmful ingredient: {ingredient_name} - {description}')

    # Step 4: Filter harmful ingredients based on user profile
    harmful_ingredients_for_user = get_harmful_ingredients(user_profile)
    harmful_ingredients_for_user_names = [ingredient[0].lower() for ingredient in harmful_ingredients_for_user]
    user_based_harmful_ingredients = [ingredient for ingredient in harmful_ingredients if ingredient[0] in harmful_ingredients_for_user_names]

    
    # Check if any user-based harmful ingredients were found
    if user_based_harmful_ingredients:
        # Print the user-based harmful ingredients in the terminal
        for ingredient in user_based_harmful_ingredients:
            print(f'Found user-based harmful ingredient: {ingredient[0]} - {ingredient[1]}')
    else:
        print('No harmful ingredients found based on user data.')
        return ['No harmful ingredients found for user']

    os.remove(filename)  # Remove the uploaded image

    # Step 5: Store harmful ingredients data in the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    for ingredient in user_based_harmful_ingredients:
        cursor.execute("INSERT INTO harmful_ingredients_data (user_id, ingredient_name, description, timestamp) VALUES (?, ?, ?, datetime('now'))",
                       (user_profile[0], ingredient[0], ingredient[1]))
    conn.commit()
    conn.close()

    return user_based_harmful_ingredients

def get_doctors_details(order_by='experience', direction='DESC'):
    conn = sqlite3.connect('doctors.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, email, qualifications, experience, (length(qualifications) - length(replace(qualifications, ',', ''))) as degrees FROM doctors ORDER BY {order_by} {direction}")
    doctors_details = [{'name': row[0], 'email': row[1], 'qualifications': row[2], 'experience': row[3], 'degrees': row[4]} for row in cursor.fetchall()]
    conn.close()
    return doctors_details

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

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
            harmful_ingredients = analyze_general_harmful_ingredients(file)

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
        kidney_problem = request.form['kidney_problem']
        heart_problem = request.form['heart_problem']
        lactose_intolerance = request.form['lactose_intolerance']
        #family doctor info
        family_doctor_name = request.form['family_doctor_name']
        family_doctor_email = request.form['family_doctor_email']

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
            cursor.execute("INSERT INTO users (name, email, age, gender, password, obese, diabetes, high_bp, high_cholesterol, fatty_liver, kidney_problem, heart_problem, lactose_intolerance, family_doctor_name, family_doctor_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (name, email, age, gender, hashed_password, obese, diabetes, high_bp, high_cholesterol, fatty_liver, kidney_problem, heart_problem, lactose_intolerance, family_doctor_name, family_doctor_email))
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
                return redirect(url_for('user'))

        # Invalid credentials or user does not exist
        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')

@app.route('/user', methods=['GET', 'POST'])
def user():
    # Define doctors_details at the start of the route
    order_by = request.args.get('order_by', 'experience')
    direction = request.args.get('direction', 'DESC')
    doctors_details = get_doctors_details(order_by, direction)

    # Check if the user is logged in
    if 'user_id' in session:
        # Retrieve the user from the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        conn.close()

        if user:
            harmful_ingredients = []
            # Retrieve the most recent harmful ingredients data from the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT ingredient_name, description FROM harmful_ingredients_data WHERE user_id = ? ORDER BY timestamp DESC", (session['user_id'],))
            harmful_ingredients = cursor.fetchall()
            conn.close()

            if request.method == 'POST':
                if 'refresh_data' in request.form:
                    # If the 'Refresh Data' button was clicked, clear the session data
                    session.pop('harmful_ingredients', None)

                    # If the 'Refresh Data' button was clicked, clear the harmful ingredients data from the database
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM harmful_ingredients_data WHERE user_id = ?", (session['user_id'],))
                    conn.commit()
                    conn.close()

                    return redirect(url_for('user'))
        
                if 'upload' in request.form:
                    # Check if a file was uploaded
                    if 'file' not in request.files:
                        error = "No file uploaded"
                        return render_template('user.html', user=user, error=error, harmful_ingredients=harmful_ingredients, doctors_details=doctors_details)

                    file = request.files['file']

                    # If the user does not select a file, the browser submits an empty file without a filename
                    if file.filename == '':
                        error = "No selected file"
                        return render_template('user.html', user=user, error=error, harmful_ingredients=harmful_ingredients, doctors_details=doctors_details)

                    # If the file exists and is allowed, proceed with OCR and detection
                    session['harmful_ingredients'] = analyze_harmful_ingredients(file, user)

                if 'doctor_email' in request.form:
                    # If the form is submitted, send the email
                    doctor_email = request.form['doctor_email']
                    if doctor_email == 'family_doctor':
                        doctor_email = user[15]  # Assuming family_doctor_email is the 14th column in the users table
                    
                    user_details = f"Name: {user[1]}\nEmail: {user[2]}\nAge: {user[3]}\nGender: {user[4]}\n"
                    health_details = f"Obese: {user[6]}\nDiabetes: {user[7]}\nHigh BP: {user[8]}\nHigh Cholesterol: {user[9]}\nFatty Liver: {user[10]}\nKidney Problem: {user[11]}\nHeart Problem: {user[12]}\nLactose Intolerance: {user[13]}\n"
                    harmful_ingredients = f"\nHarmful ingredients: \n{session.get('harmful_ingredients', [])}"
                    msg = MIMEText(user_details + health_details + f"\nHarmful ingredients: {session.get('harmful_ingredients', [])}")
                    msg['Subject'] = 'User Health Info and Harmful Ingredients'
                    msg['From'] = email
                    msg['To'] = doctor_email
                    error = send_email(msg)  # Get the error message, if any
                    if error:
                        print(f"Failed to send email: {error}")  # Print the error message
                    else:
                        print("Email sent successfully")  # Print a success message
                    return redirect(url_for('user'))  # Redirect back to the user page

                # Pass the user data and the harmful ingredients to the template
                return render_template('user.html', user=user, harmful_ingredients=session.get('harmful_ingredients', []), doctors_details=doctors_details)  # Pass the doctors' details to the template

        if not user:
            # If the user is not logged in, redirect to the login page
            return redirect(url_for('login'))

        return render_template('user.html', user=user, harmful_ingredients=harmful_ingredients, doctors_details=doctors_details)

def send_email(msg):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com') as server:
            server.login(email, password)
            server.send_message(msg)
        print("Email sent successfully")  # Print a success message
        return None  # No error
    except Exception as e:
        print(f"Error: {e}")  # Print the error message
        return str(e)  # Return the error message

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # Check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Retrieve the user from the database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        # Retrieve the updated details from the form data
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        obese = request.form['obese']
        diabetes = request.form['diabetes']
        high_bp = request.form['high_bp']
        high_cholesterol = request.form['high_cholesterol']
        fatty_liver = request.form['fatty_liver']
        kidney_problem = request.form['kidney_problem']
        heart_problem = request.form['heart_problem']
        lactose_intolerance = request.form['lactose_intolerance']

        # Update the user's details in the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET name = ?, age = ?, gender = ?, obese = ?, diabetes = ?, high_bp = ?, high_cholesterol = ?, fatty_liver = ?, kidney_problem = ?, heart_problem = ?, lactose_intolerance = ?
            WHERE id = ?
        ''', (name, age, gender, obese, diabetes, high_bp, high_cholesterol, fatty_liver, kidney_problem, heart_problem, lactose_intolerance, session['user_id']))
        conn.commit()
        conn.close()

        return redirect(url_for('user'))

    return render_template('edit_profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


