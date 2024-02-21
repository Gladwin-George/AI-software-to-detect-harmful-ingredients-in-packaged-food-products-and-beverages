from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import cv2
import easyocr
import numpy as np
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your secret key'  # Set the secret key for your Flask application to use sessions

# Step 2: Load harmful ingredients from SQLite database into a dictionary
harmful_ingredients_dict = {}
conn = sqlite3.connect('harmful_ingredients.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM harmful_ingredients")
for row in cursor.fetchall():
            ingredient_name = row[0].strip()  # Assuming ingredient name is in the first column
            harmful_ingredient_description = row[1].strip()  # Assuming harmful ingredient description is in the second column
            harmful_ingredients_dict[ingredient_name.lower()] = harmful_ingredient_description
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

            # Step 3: Identify harmful ingredients
            for ingredient_name, description in harmful_ingredients_dict.items():
                if ingredient_name in extracted_text.lower():
                    harmful_ingredients.append((ingredient_name, description))

            os.remove(filename)  # Remove the uploaded image

        return jsonify({'error': error, 'harmful_ingredients': harmful_ingredients})

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

    