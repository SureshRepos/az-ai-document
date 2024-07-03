from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename 
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient

app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Replace with a secure secret key
app.secret_key = os.getenv('SECRET_KEY')

# Azure Form Recognizer configuration
# endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
# key = os.getenv("AZURE_FORM_RECOGNIZER_API_KEY")

endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("AZURE_FORM_RECOGNIZER_API_KEY")

# Function to extract key-value pairs from PDF using Azure Form Recognizer
def extract_key_value_pairs(pdf_url):
    credential = AzureKeyCredential(key)
    form_recognizer_client = FormRecognizerClient(endpoint, credential)

    # Start the extraction process
    poller = form_recognizer_client.begin_recognize_content_from_url(pdf_url)
    form_pages = poller.result()

    # Extract key-value pairs
    key_value_pairs = {}
    for page in form_pages:
        for field in page.fields:
            if field.value:
                key_value_pairs[field.label] = field.value

    return key_value_pairs

# Route for home page with upload form
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # If file is provided, save and process it
        if file:
            # Save file to a temporary directory (you can modify the path as needed)
            file_path = os.path.join('uploads', secure_filename(file.filename))
            file.save(file_path)

            # Extract key-value pairs using Azure Form Recognizer
            extracted_data = extract_key_value_pairs(file_path)

            # Render template with extracted data
            return render_template('select_data.html', extracted_data=extracted_data, file_path=file_path)

    return render_template('upload.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_data():
    selected_data = request.form.getlist('selected_data')
    file_path = request.form['file_path']

    # Implement database submission logic here
    # Example: print selected_data and file_path
    print("Selected Data:", selected_data)
    print("File Path:", file_path)

    flash('Data submitted successfully!')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
