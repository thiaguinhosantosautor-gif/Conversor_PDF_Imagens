import os
import io
import zipfile
import shutil
from IPython.display import display, HTML
import warnings
warnings.filterwarnings('ignore')

# Colab-specific imports for interactive file operations
try:
    from google.colab import files
    from google.colab import drive
    COLAB_ENV = True
except ImportError:
    COLAB_ENV = False

def show_welcome():
    """Exibe mensagem de boas-vindas"""
    welcome_html = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;">
        <h1>📄 Conversor de PDF Completo</h1>
        <p>Converta seus PDFs para diversos formatos diretamente no Google Colab</p>
        <p style="font-size: 0.9em;">Suporta: TXT, DOCX, Excel, Imagens, HTML, OCR e muito mais!</p>
    </div>
    """
    if COLAB_ENV:
        display(HTML(welcome_html))
    else:
        print("=========================================")
        print("🚀 CONVERSOR DE PDF - GOOGLE COLAB")
        print("=========================================")
        print("Converta seus PDFs para diversos formatos")
        print("Suporta: TXT, DOCX, Excel, Imagens, HTML, OCR e muito mais!")

def display_menu():
    """Exibe o menu de opções de conversão"""
    menu = """
    =========================================
    🚀 CONVERSOR DE PDF - GOOGLE COLAB
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

def upload_pdfs(input_dir, from_drive=False):
    """
    Upload de múltiplos arquivos PDF.
    Se from_drive=True, o usuário insere caminhos do Google Drive.
    Caso contrário, usa o uploader interativo do Colab.
    Todos os PDFs são copiados para input_dir.
    """
    processed_pdf_files = []
    os.makedirs(input_dir, exist_ok=True) # Ensure input directory exists

    if from_drive and COLAB_ENV:
        print("\n📤 Digite os caminhos completos dos arquivos PDF no Google Drive (separados por vírgula), ou um caminho de diretório:")
        drive_paths_str = input("Caminhos do Drive: ").strip()
        drive_paths = [p.strip() for p in drive_paths_str.split(',') if p.strip()]

        if not drive_paths:
            print("⚠️ Nenhum caminho do Google Drive fornecido.")
            return []

        for path in drive_paths:
            # Adjust path if it's relative to MyDrive but not starting with /content/drive
            full_drive_path = os.path.join('/content/drive', path.replace('MyDrive/', 'MyDrive/', 1)) if not path.startswith('/content/drive') else path
            if os.path.isdir(full_drive_path):
                print(f"Buscando PDFs em {full_drive_path}...")
                for root, _, filenames in os.walk(full_drive_path):
                    for filename in filenames:
                        if filename.lower().endswith('.pdf'):
                            src_path = os.path.join(root, filename)
                            dest_path = os.path.join(input_dir, filename)
                            try:
                                # Use shutil.copy2 to preserve metadata
                                shutil.copy2(src_path, dest_path)
                                processed_pdf_files.append(dest_path)
                                print(f"✅ PDF copiado do Drive: {filename}")
                            except Exception as e:
                                print(f"❌ Erro ao copiar PDF '{filename}' do Drive: {e}")
            elif os.path.exists(full_drive_path) and full_drive_path.lower().endswith('.pdf'):
                filename = os.path.basename(full_drive_path)
                dest_path = os.path.join(input_dir, filename)
                try:
                    shutil.copy2(full_drive_path, dest_path)
                    processed_pdf_files.append(dest_path)
                    print(f"✅ PDF copiado do Drive: {filename}")
                except Exception as e:
                    print(f"❌ Erro ao copiar PDF '{filename}' do Drive: {e}")
            else:
                print(f"⚠️ Caminho ignorado (não é um PDF válido ou diretório existente): {path}")

    elif COLAB_ENV:
        print("\n📤 Selecione seus arquivos PDF para upload...")
        uploaded = files.upload()

        for filename, content in uploaded.items():
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(input_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(content)
                processed_pdf_files.append(filepath)
                print(f"✅ PDF carregado: {filename}")
            else:
                print(f"⚠️ Arquivo ignorado (não é PDF): {filename}")
    else:
        print("⚠️ Ambiente Colab não detectado ou from_drive=False. Não é possível fazer upload interativo.")
        return []

    return processed_pdf_files

def download_files(file_paths, output_dir, to_drive=False):
    """
    Gerencia o download ou salvamento dos arquivos convertidos.
    Se to_drive=True, os arquivos são salvos diretamente em uma subpasta dentro de output_dir no Google Drive.
    Caso contrário, um arquivo ZIP é criado em output_dir e oferecido para download local.
    """
    if not file_paths:
        print("ℹ️ Nenhum arquivo para baixar/salvar.")
        return

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    if to_drive and COLAB_ENV:
        print("\n📥 Salvando arquivos no Google Drive...")
        subfolder_name = input("📁 Digite o nome da subpasta no Google Drive para salvar (padrão: Converted_Files): ").strip()
        if not subfolder_name:
            subfolder_name = "Converted_Files"

        drive_save_path = os.path.join(output_dir, subfolder_name)
        os.makedirs(drive_save_path, exist_ok=True)

        saved_count = 0
        for file_path in file_paths:
            if os.path.exists(file_path):
                dest_path = os.path.join(drive_save_path, os.path.basename(file_path))
                try:
                    shutil.copy2(file_path, dest_path)
                    print(f"✅ Salvo no Drive: {os.path.basename(file_path)} -> {drive_save_path}")
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Erro ao salvar '{os.path.basename(file_path)}' no Drive: {str(e)}")
            else:
                print(f"⚠️ Arquivo não encontrado para salvar: {file_path}")
        print(f"🎉 Total de {saved_count} arquivo(s) salvo(s) no Google Drive.")
    elif COLAB_ENV:
        zip_filename = "converted_files.zip"
        zip_filepath = os.path.join(output_dir, zip_filename)

        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for file in file_paths:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))
                else:
                    print(f"⚠️ Arquivo não encontrado para adicionar ao ZIP: {file}")

        print(f"📥 Arquivo ZIP pronto para download local: {zip_filepath}")
        files.download(zip_filepath)
    else:
        print("⚠️ Ambiente Colab não detectado ou to_drive=False. Não é possível baixar/salvar interativamente.")
        # In a non-Colab env, just print paths or something
        print("Arquivos convertidos estão disponíveis em:")
        for fp in file_paths:
            print(f"- {fp}")
