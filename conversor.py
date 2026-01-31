import os
import io
import zipfile
import PyPDF2
from pdf2docx import Converter
import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# ==================== FUNÇÕES DE CONVERSÃO ====================
def pdf_to_text(pdf_path):
    """Converte PDF para arquivo de texto"""
    output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '.txt')}"

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""

            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

            # Salvar texto
            with open(output_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text)

            print(f"✅ PDF convertido para texto: {output_path}")
            return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para texto: {str(e)}")
        return None

def pdf_to_word(pdf_path):
    """Converte PDF para Word (.docx)"""
    try:
        output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '.docx')}"

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
    output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '.xlsx')}"

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
    """Converte cada página do PDF para imagem"""
    try:
        base_name = os.path.basename(pdf_path).replace('.pdf', '')
        output_dir = f"output_files/{base_name}_images"
        os.makedirs(output_dir, exist_ok=True)

        # Converter PDF para imagens
        images = convert_from_path(pdf_path, dpi=200)

        image_paths = []
        for i, image in enumerate(images):
            image_path = f"{output_dir}/pagina_{i+1}.jpg"
            image.save(image_path, 'JPEG', quality=95)
            image_paths.append(image_path)

        # Criar arquivo ZIP com as imagens
        zip_path = f"output_files/{base_name}_images.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img_path in image_paths:
                zipf.write(img_path, os.path.basename(img_path))

        print(f"✅ PDF convertido para {len(images)} imagens")
        return zip_path

    except Exception as e:
        print(f"❌ Erro na conversão para imagens: {str(e)}")
        return None

def pdf_to_html(pdf_path):
    """Converte PDF para HTML simples"""
    output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '.html')}"

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

            with open(output_path, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)

            print(f"✅ PDF convertido para HTML: {output_path}")
            return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para HTML: {str(e)}")
        return None

def pdf_to_pdfa(pdf_path):
    """Converte para PDF/A (padrão arquivável)"""
    try:
        from PyPDF2 import PdfReader, PdfWriter

        output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '_pdfa.pdf')}"

        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Adicionar metadados
        writer.add_metadata({
            '/Title': os.path.basename(pdf_path),
            '/Creator': 'PDF Converter Colab',
            '/Producer': 'PyPDF2',
            '/CreationDate': 'D:20240101000000'
        })

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        print(f"✅ PDF convertido para PDF/A: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Erro na conversão para PDF/A: {str(e)}")
        return None

def pdf_ocr(pdf_path):
    """Aplica OCR no PDF para extrair texto de imagens"""
    try:
        base_name = os.path.basename(pdf_path).replace('.pdf', '')
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)

        # Converter PDF para imagens
        images = convert_from_path(pdf_path, dpi=300)

        text_content = ""
        for i, image in enumerate(images):
            # Aplicar OCR em cada imagem
            text = pytesseract.image_to_string(image, lang='por+eng')
            text_content += f"\n\n--- Página {i+1} ---\n\n{text}"

        # Salvar texto extraído
        output_path = f"output_files/{base_name}_ocr.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # Criar novo PDF com texto
        pdf_output_path = f"output_files/{base_name}_ocr.pdf"
        c = canvas.Canvas(pdf_output_path, pagesize=letter)

        lines = text_content.split('\n')
        y = 750
        for line in lines:
            if y < 50:  # Nova página
                c.showPage()
                y = 750
            c.drawString(50, y, line[:100])  # Limita o tamanho da linha
            y -= 15

        c.save()

        print(f"✅ OCR aplicado e PDF criado: {pdf_output_path}")
        return pdf_output_path

    except Exception as e:
        print(f"❌ Erro no OCR: {str(e)}")
        print("⚠️ Certifique-se de que Tesseract está instalado corretamente")
        return None

def extract_images_from_pdf(pdf_path):
    """Extrai todas as imagens de um PDF"""
    output_dir = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '_extracted_images')}"
    os.makedirs(output_dir, exist_ok=True)

    try:
        pdf_document = fitz.open(pdf_path)
        image_paths = []

        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                image_ext = base_image["ext"]
                image_filename = f"{output_dir}/pagina_{page_num+1}_img_{img_index+1}.{image_ext}"

                with open(image_filename, "wb") as image_file:
                    image_file.write(image_bytes)

                image_paths.append(image_filename)

        pdf_document.close()

        if image_paths:
            # Criar ZIP com imagens extraídas
            zip_path = f"{output_dir}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for img_path in image_paths:
                    zipf.write(img_path, os.path.basename(img_path))

            print(f"✅ {len(image_paths)} imagens extraídas do PDF")
            return zip_path
        else:
            print("ℹ️ Nenhuma imagem encontrada no PDF")
            return None

    except Exception as e:
        print(f"❌ Erro na extração de imagens: {str(e)}")
        return None

def merge_pdfs(pdf_files):
    """Mescla múltiplos PDFs em um único arquivo"""
    from PyPDF2 import PdfMerger

    output_path = "output_files/merged_document.pdf"

    try:
        merger = PdfMerger()

        for pdf_file in pdf_files:
            merger.append(pdf_file)

        merger.write(output_path)
        merger.close()

        print(f"✅ {len(pdf_files)} PDFs mesclados em: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Erro ao mesclar PDFs: {str(e)}")
        return None

def split_pdf(pdf_path):
    """Divide um PDF em páginas individuais"""
    from PyPDF2 import PdfReader, PdfWriter

    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = f"output_files/{base_name}_pages"
    os.makedirs(output_dir, exist_ok=True)

    try:
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        individual_files = []

        for i in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])

            output_file = f"{output_dir}/pagina_{i+1}.pdf"
            with open(output_file, "wb") as output_pdf:
                writer.write(output_pdf)

            individual_files.append(output_file)

        # Criar arquivo ZIP com todas as páginas
        zip_path = f"{output_dir}.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in individual_files:
                zipf.write(file_path, os.path.basename(file_path))

        print(f"✅ PDF dividido em {total_pages} páginas individuais")
        return zip_path

    except Exception as e:
        print(f"❌ Erro ao dividir PDF: {str(e)}")
        return None

def compress_pdf(pdf_path):
    """Comprime um PDF reduzindo qualidade de imagens"""
    try:
        output_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', '_compressed.pdf')}"

        doc = fitz.open(pdf_path)

        # Configuração de compressão
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Reduz resolução
            page.insert_image(page.rect, pixmap=pix)  # Reinsere imagem comprimida

        # Salva com compressão
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

        original_size = os.path.getsize(pdf_path) / 1024  # KB
        new_size = os.path.getsize(output_path) / 1024  # KB
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
    try:
        with pdfplumber.open(pdf_path) as pdf:
            tables_found = 0
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for j, table in enumerate(tables):
                    if table:
                        df = pd.DataFrame(table)
                        csv_path = f"output_files/{os.path.basename(pdf_path).replace('.pdf', f'_page{i+1}_table{j+1}.csv')}"
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

print("✅ conversor.py atualizado com sucesso!")
