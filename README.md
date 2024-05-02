# AI software to detect harmful ingredients in packaged food products and beverages

This website is a Flask web application that utilizes optical character recognition (OCR) to analyze harmful ingredients from packaged food products and beverages from ingredients label images. It can detect harmful ingredients in food products and provide personalized health recommendations based on user profiles.

## Features

- **OCR Analysis**: Extracts text from uploaded images using Tesseract-OCR.
- **Harmful Ingredient Detection**: Identifies harmful ingredients in food products based on extracted text.
- **User Profiles**: Allows users to register and create profiles with personal health information.
- **Personalized Recommendations**: Provides personalized health recommendations based on user profiles.
- **Email Integration**: Sends health reports to family doctors or specified email addresses.

## Installation

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/Gladwin-George/AI-software-to-detect-harmful-ingredients-in-packaged-food-products-and-beverages.git
   ```

2. **Install Dependencies**: 
   ```python
   pip install -r requirements.txt
   ```

3. **Set Up Easyocr / Tesseract-OCR**: 

   **For easyocr**:
    ```python
    pip install easyocr
    ```

   **For Tesseract-OCR**:

    Download and install Tesseract-OCR from [here](https://github.com/tesseract-ocr/tesseract).
    Set the `pytesseract.tesseract_cmd` variable in `app.py` to the path where Tesseract is installed.


5. **Set Up Email Configuration**: 
   - Create a `.env` file in the project directory.
   - Add your email credentials:
     ```
     EMAIL=your_email@example.com
     EMAIL_PASSWORD=your_email_password
     ```

## Usage

1. **Run the Flask Application**: 
   ```python
   python app.py
   ```

2. **Access the Application**: 
    Open a web browser and go to `http://127.0.0.1:5000/` or `http://localhost:5000/`.

3. **Register and Login**: 
    Register as a new user or login with existing credentials to access the user dashboard.

4. **Upload Images**: 
    After logging in, upload images for OCR processing.

5. **Edit Profile**: 
    Users can edit their profiles to update personal information and health conditions.

6. **Logout**: 
    Users can logout from their accounts by clicking on the logout button.

## Customization

- **Database Schema**: 
  - Modify the SQLite databases schema according to your application's requirements.

- **Email Configuration**: 
  - Customize the email configuration in `app.py` based on your email service provider.

- **User Interface**: 
  - Customize the HTML templates (`templates/`) and CSS styles (`static/css/`) to match your desired UI/UX.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
