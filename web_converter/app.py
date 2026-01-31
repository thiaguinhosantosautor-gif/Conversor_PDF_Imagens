import os
import shutil
import warnings
import logging

from flask import Flask, request, render_template, send_file, jsonify
from flask_ngrok import run_with_ngrok # Importado para expor a app no Colab

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import functions from utils and conversor
from utils import create_directories, upload_pdfs, download_files
from conversor import (
    pdf_to_text,
    pdf_to_word,
    pdf_to_excel,
    pdf_to_images,
    pdf_to_html,
    pdf_to_pdfa,
    pdf_ocr,
    extract_images_from_pdf,
    merge_pdfs,
    split_pdf,
    compress_pdf,
    pdf_to_csv_conversion
)

# Ignorar warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, template_folder='templates', static_folder='static')
run_with_ngrok(app) # Habilita o ngrok para a aplicação Flask

# Ensure directories exist when the app starts
create_directories()

# Mapping conversion choice to function
CONVERSION_FUNCTIONS = {
    '1': pdf_to_text,
    '2': pdf_to_word,
    '3': pdf_to_excel,
    '4': pdf_to_images,
    '5': pdf_to_html,
    '6': pdf_to_pdfa,
    '7': pdf_ocr,
    '8': extract_images_from_pdf,
    '9': pdf_to_csv_conversion,
    '11': split_pdf,
    '12': compress_pdf,
}

@app.route('/')
def index():
    logging.info("Serving index.html")
    return render_template('index.html')

@app.route('/upload_and_convert', methods=['POST'])
def upload_and_convert():
    logging.info("Received upload and convert request")
    if 'pdf_file' not in request.files:
        logging.error("No PDF file part in the request")
        return jsonify({'error': 'No PDF file part'}), 400

    pdf_file = request.files['pdf_file']
    conversion_choice = request.form.get('conversion_choice')
    
    if pdf_file.filename == '':
        logging.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if not conversion_choice:
        logging.error("No conversion choice provided")
        return jsonify({'error': 'No conversion choice provided'}), 400

    if pdf_file and pdf_file.filename.lower().endswith('.pdf'):
        try:
            uploaded_files = upload_pdfs([pdf_file])
            if not uploaded_files:
                logging.error("Failed to upload PDF")
                return jsonify({'error': 'Failed to upload PDF'}), 500
            
            input_pdf_path = uploaded_files[0]
            converted_files = []

            if conversion_choice == '10': 
                logging.warning("Merge PDF option selected but only one file uploaded. Skipping merge for now.")
                return jsonify({'error': 'Merging PDFs requires multiple files, single file upload endpoint used.'}), 400
            elif conversion_choice == '13': 
                logging.info(f"Converting {input_pdf_path} to all formats")
                conversions = [
                    pdf_to_text, pdf_to_word, pdf_to_excel, pdf_to_images, 
                    pdf_to_html, pdf_to_pdfa, pdf_ocr, pdf_to_csv_conversion
                ]
                for func in conversions:
                    result = func(input_pdf_path)
                    if result:
                        if isinstance(result, list): 
                            converted_files.extend(result)
                        else:
                            converted_files.append(result)
            elif conversion_choice in CONVERSION_FUNCTIONS:
                logging.info(f"Converting {input_pdf_path} using option {conversion_choice}")
                func = CONVERSION_FUNCTIONS[conversion_choice]
                result = func(input_pdf_path)
                if result:
                    if isinstance(result, list):
                        converted_files.extend(result)
                    else:
                        converted_files.append(result)
            else:
                logging.error(f"Invalid conversion choice: {conversion_choice}")
                return jsonify({'error': 'Invalid conversion choice'}), 400

            if converted_files:
                zip_file_path = download_files(converted_files)
                logging.info(f"Conversion successful, sending {zip_file_path} for download")
                return send_file(zip_file_path, as_attachment=True, download_name='converted_files.zip')
            else:
                logging.warning("No files converted successfully.")
                return jsonify({'error': 'No files converted successfully.'}), 500

        except Exception as e:
            logging.exception(f"Error during conversion: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if 'input_pdf_path' in locals() and os.path.exists(input_pdf_path):
                os.remove(input_pdf_path)
                logging.info(f"Cleaned up input file: {input_pdf_path}")

    return jsonify({'error': 'Only PDF files are accepted.'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
