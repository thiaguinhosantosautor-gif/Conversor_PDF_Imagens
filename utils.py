import os
import io
import zipfile
import shutil # Importado para copiar arquivos

def create_directories():
    """Cria diretórios para organização"""
    os.makedirs("input_pdfs", exist_ok=True)
    os.makedirs("output_files", exist_ok=True)
    os.makedirs("temp_files", exist_ok=True)
    print("📁 Diretórios criados com sucesso!")

def display_menu():
    """Exibe o menu de opções de conversão"""
    menu = """
    =========================================
    🚀 CONVERSOR DE PDF
    =========================================
    Escolha o formato de conversão:

    1. PDF para Texto (.txt)
    2. PDF para Word (.docx)
    3. PDF para Excel (.xlsx)
    4. PDF para Imagens (.jpg/.png)
    5. PDF para HTML
    6. PDF para PDF/A (arquivo padrão)
    7. PDF para PDF com OCR (reconhecimento de texto)
    8. Extrair imagens do PDF
    9. PDF para CSV
    10. Mesclar múltiplos PDFs
    11. Dividir PDF por páginas
    12. Comprimir PDF
    13. Converter todas as opções

    0. Sair

    =========================================
    """
    print(menu)

def upload_pdfs(files_source=None):
    """Aceita uma lista de caminhos de arquivos PDF ou objetos de arquivo e os copia/salva para input_pdfs/"""
    if files_source is None:
        print("⚠️ `upload_pdfs` foi chamada sem arquivos. Forneça caminhos ou objetos de arquivo.")
        return []

    processed_pdf_files = []
    for item in files_source:
        filepath = None
        if isinstance(item, str): # É um caminho de arquivo (string)
            original_filepath = item
            if os.path.exists(original_filepath) and original_filepath.lower().endswith('.pdf'):
                filename = os.path.basename(original_filepath)
                destination_filepath = f"input_pdfs/{filename}"

                if os.path.abspath(original_filepath) == os.path.abspath(destination_filepath):
                    filepath = original_filepath
                    print(f"✅ PDF já está no diretório de entrada: {filename}")
                else:
                    shutil.copy(original_filepath, destination_filepath)
                    filepath = destination_filepath
                    print(f"✅ PDF carregado e copiado: {filename}")
            else:
                print(f"⚠️ Arquivo ignorado (não encontrado ou não é PDF): {original_filepath}")

        elif hasattr(item, 'read') and hasattr(item, 'filename'): # É um objeto de arquivo (e.g., de upload web)
            filename = item.filename # Supondo que o objeto tenha um atributo 'filename'
            if filename.lower().endswith('.pdf'):
                destination_filepath = f"input_pdfs/{filename}"
                with open(destination_filepath, "wb") as f:
                    f.write(item.read())
                filepath = destination_filepath
                print(f"✅ PDF carregado do objeto de arquivo: {filename}")
            else:
                print(f"⚠️ Arquivo ignorado (não é PDF): {filename}")
        else:
            print(f"⚠️ Item ignorado (tipo desconhecido): {type(item)}")

        if filepath: # Adicionar apenas se o arquivo foi processado com sucesso
            processed_pdf_files.append(filepath)

    return processed_pdf_files

def download_files(file_paths):
    """Cria um arquivo ZIP com os arquivos processados e retorna o caminho para ele."""
    zip_filename = "converted_files.zip"
    output_zip_path = os.path.join("output_files", zip_filename)

    # Garante que o diretório de saída exista
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file in file_paths:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))

    print(f"📥 Arquivo ZIP com os resultados salvo em: {output_zip_path}")
    return output_zip_path

# show_welcome function removed as per instruction

print("✅ `utils.py` atualizado para neutralidade de ambiente.")
