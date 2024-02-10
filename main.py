from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import easyocr
import numpy as np
import csv
import os

app = Flask(__name__)
app.secret_key = 'your secret key'  # Set the secret key for your Flask application to use sessions

# Load harmful ingredients from CSV into a dictionary
harmful_ingredients_dict = {}
with open('harmful_ingredients.csv', 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the first row (headings)
    for row in csv_reader:
        if len(row) >= 2 and row[0] and row[1]:  # Check if both columns have data
            ingredient_name = row[0].strip().lower()  # Assuming ingredient name is in the first column
            harmful_ingredient_description = row[1].strip()  # Assuming harmful ingredient description is in the second column
            harmful_ingredients_dict[ingredient_name] = harmful_ingredient_description

@app.route('/', methods=['GET', 'POST'])
def index():
    harmful_ingredients = session.get('harmful_ingredients', None)
    session.pop('harmful_ingredients', None)  # Clear the session after retrieving the data

    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(url_for('index', error="No file uploaded"))

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(url_for('index', error="No selected file"))

        # If the file exists and is allowed, proceed with OCR and detection
        if file:
            filename = 'uploaded_image.jpg'
            file.save(filename)

            # Step 1: Extract text from the image
            img = cv2.imread(filename)
            reader = easyocr.Reader(['en'])
            text_results = reader.readtext(filename)
            extracted_text = ' '.join([result[1] for result in text_results])

            # Step 3: Identify harmful ingredients
            found_harmful_ingredients = []
            for ingredient_name, description in harmful_ingredients_dict.items():
                if ingredient_name in extracted_text.lower():
                    found_harmful_ingredients.append((ingredient_name, description))

            os.remove(filename)  # Remove the uploaded image

            session['harmful_ingredients'] = found_harmful_ingredients  # Store the harmful ingredients in the session
            return redirect(url_for('show_harmful_ingredients'))

    # Clear harmful ingredients when rendering the index page
    return render_template('index.html', harmful_ingredients=harmful_ingredients)

@app.route('/harmful-ingredients')
def show_harmful_ingredients():
    harmful_ingredients = session.get('harmful_ingredients', [])
    session.pop('harmful_ingredients', None)  # Clear the session after retrieving the data
    return render_template('index.html', harmful_ingredients=harmful_ingredients) 


if __name__ == '__main__':
    app.run(debug=True)