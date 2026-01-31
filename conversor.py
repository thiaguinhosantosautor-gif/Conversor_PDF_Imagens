import os
import io
import zipfile
import shutil
import re
import warnings
from concurrent.futures import ProcessPoolExecutor
from tqdm.auto import tqdm

# PDF Libraries
import PyPDF2
from pdf2docx import Converter
import pdfplumber
from pdf2image import convert_from_bytes # Changed from convert_from_path for parallel processing
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
from PIL import Image
import pandas as pd

warnings.filterwarnings('ignore')

# Variável global para o caminho base do Drive, a ser definida por main.py
GLOBAL_BASE_DRIVE_PATH = '/content/drive/MyDrive/DESMONTE_V01/' # Default, será sobrescrito

def set_global_base_drive_path(path):
    global GLOBAL_BASE_DRIVE_PATH
    GLOBAL_BASE_DRIVE_PATH = path

def get_base_drive_path():
    return GLOBAL_BASE_DRIVE_PATH

# ==================== FUNÇÕES AUXILIARES PARA PROCESSAMENTO PARALELO ====================
def _convert_single_page_to_image(page_info):
    """Helper to convert a single PDF page to an image."""
    pdf_bytes, page_num, dpi, output_dir = page_info
    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=page_num, last_page=page_num)
        if images:
            image = images[0]
            image_path = f"{output_dir}/pagina_{page_num}.jpg"
            image.save(image_path, 'JPEG', quality=95)
            return image_path
    except Exception as e:
        print(f"❌ Erro ao converter página {page_num} para imagem: {str(e)}")
    return None

def _ocr_single_page(page_info):
    """Helper to perform OCR on a single PDF page image and return text."""
    pdf_bytes_data, page_num, dpi, lang = page_info
    try:
        images = convert_from_bytes(pdf_bytes_data, dpi=dpi, first_page=page_num, last_page=page_num)
        if images:
            image = images[0]
            text = pytesseract.image_to_string(image, lang=lang)
            return f"""
--- Página {page_num} ---
{text}
"""
    except Exception as e:
        return f"""
--- Erro na Página {page_num} (OCR): {str(e)} ---
"""
    return ""

# ==================== FUNÇÕES DE CONVERSÃO ====================
def pdf_to_text(pdf_path):
    """Converte PDF para arquivo de texto usando pdfplumber"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '.txt'))

    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text(x_tolerance=1) if page.extract_text() else '' # x_tolerance para melhor fusão de texto

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

        print(f"✅ PDF convertido para texto com pdfplumber: {output_path}")
        return output_path

    except PyPDF2.errors.PdfReadError:
        print(f"❌ Erro: O PDF '{os.path.basename(pdf_path)}' parece estar corrompido ou protegido por senha e não pode ser lido.")
        return None
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo PDF '{os.path.basename(pdf_path)}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado na conversão para texto: {str(e)}")
        return None

def pdf_to_word(pdf_path):
    """Converte PDF para Word (.docx)"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '.docx'))

    try:
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()

        print(f"✅ PDF convertido para Word: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para Word: {str(e)}")
        return None

def pdf_to_excel(pdf_path):
    """Extrai tabelas do PDF para Excel"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '.xlsx'))

    try:
        all_tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()

                for table_num, table in enumerate(tables):
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df['PDF_Page'] = page_num + 1
                        all_tables.append(df)

        if all_tables:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for i, df in enumerate(all_tables):
                    df.to_excel(writer, sheet_name=f'Tabela_{i+1}', index=False)

            print(f"✅ Tabelas extraídas para Excel: {output_path}")
            return output_path
        else:
            print("ℹ️ Nenhuma tabela encontrada no PDF")
            return None

    except Exception as e:
        print(f"❌ Erro na extração para Excel: {str(e)}")
        return None

def pdf_to_images(pdf_path):
    """Converte cada página do PDF para imagem usando processamento paralelo e barra de progresso"""
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_images")
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes_data = f.read()

        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes_data))
        total_pages = len(reader.pages)

        image_paths = []
        tasks = [ (pdf_bytes_data, i + 1, 200, output_dir) for i in range(total_pages) ]

        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(_convert_single_page_to_image, tasks), total=total_pages, desc=f"Convertendo {base_name} para imagens"))
            for path in results:
                if path:
                    image_paths.append(path)

        if not image_paths:
            print("ℹ️ Nenhuma imagem foi convertida.")
            return None

        zip_path = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_images.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in image_paths:
                zipf.write(img_path, os.path.basename(img_path))

        print(f"✅ PDF convertido para {len(image_paths)} imagens (paralelo): {zip_path}")
        return zip_path

    except Exception as e:
        print(f"❌ Erro na conversão para imagens (paralelo): {str(e)}")
        return None

def pdf_to_html(pdf_path):
    """Converte PDF para HTML simples"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '.html'))

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset=\"UTF-8\">
                <title>PDF Convertido</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
                    .page { margin-bottom: 50px; padding: 20px; border-bottom: 1px solid #ccc; }
                    .page-number { color: #666; font-size: 0.9em; }
                </style>
            </head>
            <body>
            """

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                html_content += f"""
                <div class=\"page\">
                    <div class=\"page-number\">Página {page_num + 1}</div>
                    <pre>{text}</pre>
                </div>
                """

            html_content += "</body></html>"

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)

            print(f"✅ PDF convertido para HTML: {output_path}")
            return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para HTML: {str(e)}")
        return None

def pdf_to_pdfa(pdf_path):
    """Converte para PDF/A (padrão arquivável) usando PyMuPDF (fitz)"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '_pdfa.pdf'))

    try:
        doc = fitz.open(pdf_path)
        doc.convert_to_pdfa(level=2, conformance="b", saveinfo=True, garbage=4, clean=True, deflating=True, savealpha=True, linear=True)
        doc.save(output_path, garbage=4, clean=True, deflating=True)
        doc.close()

        print(f"✅ PDF convertido para PDF/A com fitz: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para PDF/A com fitz: {str(e)}")
        return None

def pdf_ocr(pdf_path):
    """Aplica OCR no PDF para extrair texto de imagens usando processamento paralelo e barra de progresso"""
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_files_dir = os.path.join(get_base_drive_path(), "output_files")
    os.makedirs(output_files_dir, exist_ok=True)

    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes_data = f.read()

        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes_data))
        total_pages = len(reader.pages)

        tasks = [ (pdf_bytes_data, i + 1, 300, 'por+eng') for i in range(total_pages) ]

        text_content_parts = []
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(_ocr_single_page, tasks), total=total_pages, desc=f"Processando OCR para {base_name}"))
            for part in results:
                text_content_parts.append(part)

        text_content = "".join(text_content_parts)

        output_txt_path = os.path.join(output_files_dir, f"{base_name}_ocr.txt")
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"✅ Texto OCR extraído salvo em: {output_txt_path}")

        pdf_output_path = os.path.join(output_files_dir, f"{base_name}_ocr.pdf")
        c = canvas.Canvas(pdf_output_path, pagesize=letter)

        lines = text_content.split('\n')
        y = 750
        for line in lines:
            if y < 50:
                c.showPage()
                y = 750
            display_line = line[:80]
            c.drawString(50, y, display_line)
            y -= 15

        c.save()

        print(f"✅ PDF pesquisável com OCR criado: {pdf_output_path}")
        return pdf_output_path

    except Exception as e:
        print(f"❌ Erro no OCR com processamento paralelo: {str(e)}")
        print("⚠️ Certifique-se de que Tesseract está instalado corretamente")
        return None

def extract_images_from_pdf(pdf_path):
    """Extrai todas as imagens de um PDF"""
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_extracted_images")
    os.makedirs(output_dir, exist_ok=True)

    try:
        pdf_document = fitz.open(pdf_path)
        image_paths = []

        for page_num in tqdm(range(len(pdf_document)), desc=f"Extraindo imagens de {os.path.basename(pdf_path)}"):
            page = pdf_document[page_num]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                image_ext = base_image["ext"]
                image_filename = os.path.join(output_dir, f"pagina_{page_num+1}_img_{img_index+1}.{image_ext}")

                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)

                image_paths.append(image_filename)

        pdf_document.close()

        if image_paths:
            zip_path = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_images.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in image_paths:
                    zipf.write(img_path, os.path.basename(img_path))

            print(f"✅ {len(image_paths)} imagens extraídas do PDF: {zip_path}")
            return zip_path
        else:
            print("ℹ️ Nenhuma imagem encontrada no PDF")
            return None

    except Exception as e:
        print(f"❌ Erro na extração de imagens: {str(e)}")
        return None

def merge_pdfs(pdf_files):
    """Mescla múltiplos PDFs em um único arquivo usando PyMuPDF (fitz) com barra de progresso"""
    output_path = os.path.join(get_base_drive_path(), "output_files", "merged_document.pdf")

    try:
        output_pdf = fitz.open()

        for pdf_file in tqdm(pdf_files, desc="Mesclando PDFs"):
            input_pdf = fitz.open(pdf_file)
            output_pdf.insert_pdf(input_pdf)
            input_pdf.close()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_pdf.save(output_path)
        output_pdf.close()

        print(f"✅ {len(pdf_files)} PDFs mesclados em: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Erro ao mesclar PDFs com fitz: {str(e)}")
        return None

def split_pdf(pdf_path):
    """Divide um PDF em páginas individuais usando PyMuPDF (fitz) com barra de progresso"""
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_pages")
    os.makedirs(output_dir, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        individual_files = []

        for i in tqdm(range(total_pages), desc=f"Dividindo {base_name}"):
            output_pdf = fitz.open()
            output_pdf.insert_pdf(doc, from_page=i, to_page=i)

            output_file = os.path.join(output_dir, f"pagina_{i+1}.pdf")
            output_pdf.save(output_file)
            output_pdf.close()

            individual_files.append(output_file)

        doc.close()

        zip_path = os.path.join(get_base_drive_path(), "output_files", f"{base_name}_pages.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in individual_files:
                zipf.write(file_path, os.path.basename(file_path))

        print(f"✅ PDF dividido em {total_pages} páginas individuais com fitz: {zip_path}")
        return zip_path

    except Exception as e:
        print(f"❌ Erro ao dividir PDF com fitz: {str(e)}")
        return None

def compress_pdf(pdf_path):
    """Comprime um PDF reduzindo qualidade de imagens com barra de progresso"""
    output_path = os.path.join(get_base_drive_path(), "output_files", os.path.basename(pdf_path).replace('.pdf', '_compressed.pdf'))

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        for i in tqdm(range(total_pages), desc=f"Comprimindo {os.path.basename(pdf_path)}"):
            page = doc[i]
            # The actual compression happens on doc.save, this loop is just for progress indication.

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path, garbage=4, deflate=True, clean=True, super_fast=True)
        doc.close()

        original_size = os.path.getsize(pdf_path) / 1024 # KB
        new_size = os.path.getsize(output_path) / 1024 # KB
        reduction = ((original_size - new_size) / original_size) * 100

        print(f"✅ PDF comprimido: {output_path}")
        print(f"   Tamanho original: {original_size:.2f} KB")
        print(f"   Novo tamanho: {new_size:.2f} KB")
        print(f"   Redução: {reduction:.1f}%")

        return output_path

    except Exception as e:
        print(f"❌ Erro na compressão: {str(e)}")
        return None

def pdf_to_csv_conversion(pdf_path):
    """Extrai tabelas do PDF para CSV"""
    converted_csv_paths = []
    output_dir = os.path.join(get_base_drive_path(), "output_files")
    os.makedirs(output_dir, exist_ok=True)
    try:
        with pdfplumber.open(pdf_path) as pdf:
            tables_found = 0
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if table:
                        df = pd.DataFrame(table)
                        csv_path = os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', f'_page{i+1}_table{j+1}.csv'))
                        df.to_csv(csv_path, index=False, encoding='utf-8')
                        converted_csv_paths.append(csv_path)
                        tables_found += 1
                        print(f"✅ Tabela salva como CSV: {csv_path}")
            if tables_found == 0:
                print("ℹ️ Nenhuma tabela encontrada para exportar para CSV.")
            return converted_csv_paths
    except Exception as e:
        print(f"❌ Erro na extração para CSV: {str(e)}")
        return []
