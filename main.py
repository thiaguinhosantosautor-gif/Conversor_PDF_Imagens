import os
import shutil
import warnings

# Ignorar warnings
warnings.filterwarnings('ignore')

# NOTE: Functions from utils.py and conversor.py are assumed to be loaded into the global scope
#       by preceding exec() calls in the notebook. Therefore, no direct imports here.

# Definir o caminho base no Google Drive
# Esta variável será usada por set_global_base_drive_path() em conversor.py
# It will be defined in the main execution cell's scope, and override_get_base_drive_path will update it.
# BASE_DRIVE_PATH = '/content/drive/MyDrive/DESMONTE_V01/' # Removed from here, defined in execution cell

# Esta função será chamada externamente após a execução dos scripts
def override_get_base_drive_path(new_path):
    global BASE_DRIVE_PATH # Refers to BASE_DRIVE_PATH in the notebook's global scope
    BASE_DRIVE_PATH = new_path
    # set_global_base_drive_path comes from conversor.py, assumed to be in global scope
    set_global_base_drive_path(new_path)

def main_converter():
    """Função principal do conversor"""

    print("\nℕ Inicializando Conversor de PDF...")

    # Criar diretórios no caminho base do Drive
    input_pdfs_dir = os.path.join(BASE_DRIVE_PATH, "input_pdfs") # Uses global BASE_DRIVE_PATH
    output_files_dir = os.path.join(BASE_DRIVE_PATH, "output_files") # Uses global BASE_DRIVE_PATH
    temp_files_dir = os.path.join(BASE_DRIVE_PATH, "temp_files") # Uses global BASE_DRIVE_PATH

    os.makedirs(input_pdfs_dir, exist_ok=True)
    os.makedirs(output_files_dir, exist_ok=True)
    os.makedirs(temp_files_dir, exist_ok=True)
    print(f"◒ Diretórios criados/verificados em: {BASE_DRIVE_PATH}")


    while True:
        # As funções display_menu, upload_pdfs, download_files e as de conversão
        # serão acessíveis porque utils.py e conversor.py foram exec()tados antes.
        display_menu() # Assumed to be in global scope from utils.py

        try:
            choice = input("\n№ Digite o número da opção desejada: ").strip()

            if choice == '0':
                print("👋 Saindo do conversor...")
                break

            pdf_files = []
            # A função upload_pdfs agora sempre usa o Google Drive
            pdf_files = upload_pdfs(input_pdfs_dir, from_drive=True)

            if not pdf_files:
                print("⚠️ Nenhum PDF válido foi carregado. Retornando ao menu principal.")
                continue

            converted_files = []

            if choice == '10':
                if len(pdf_files) > 1:
                    print(f"\n📄 Processando {len(pdf_files)} PDFs para mesclagem...")
                    result = merge_pdfs(pdf_files) # Assumed to be in global scope from conversor.py
                    if result:
                        converted_files.append(result)
                else:
                    print("⚠️ É necessário pelo menos 2 PDFs para mesclar. Por favor, selecione mais arquivos.")

            else:
                for pdf_file in pdf_files:
                    print(f"\n📄 Processando: {os.path.basename(pdf_file)}")

                    if choice == '1':
                        result = pdf_to_text(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '2':
                        result = pdf_to_word(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '3':
                        result = pdf_to_excel(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '4':
                        result = pdf_to_images(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '5':
                        result = pdf_to_html(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '6':
                        result = pdf_to_pdfa(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '7':
                        result = pdf_ocr(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '8':
                        result = extract_images_from_pdf(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '9':
                        results_csv = pdf_to_csv_conversion(pdf_file) # Assumed to be in global scope from conversor.py
                        if results_csv:
                            converted_files.extend(results_csv)

                    elif choice == '11':
                        result = split_pdf(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '12':
                        result = compress_pdf(pdf_file) # Assumed to be in global scope from conversor.py
                        if result: converted_files.append(result)

                    elif choice == '13':
                        print("ℕ Convertendo para todos os formatos...")
                        conversions = [
                            ('Texto', pdf_to_text),
                            ('Word', pdf_to_word),
                            ('Excel', pdf_to_excel),
                            ('Imagens', pdf_to_images),
                            ('HTML', pdf_to_html),
                            ('PDF/A', pdf_to_pdfa),
                            ('OCR', pdf_ocr)
                        ]

                        for name, func in conversions:
                            print(f"\n  ℕ Convertendo para {name}...")
                            result = func(pdf_file)
                            if result:
                                if isinstance(result, list):
                                    converted_files.extend(result)
                                else:
                                    converted_files.append(result)
                    else:
                        print("❌ Opção inválida! Por favor, escolha uma opção do menu.")
                        continue

            if converted_files:
                print(f"\n✅ Total de {len(converted_files)} arquivo(s) convertido(s) com sucesso!")

                # download_files agora sempre salva no Drive
                download_files(converted_files, output_files_dir, to_drive=True) # Assumed to be in global scope from utils.py

            print("\n🔧 Limpando arquivos temporários...")
            if os.path.exists(temp_files_dir):
                shutil.rmtree(temp_files_dir)
                os.makedirs(temp_files_dir)

            if os.path.exists(input_pdfs_dir):
                for item in os.listdir(input_pdfs_dir):
                    item_path = os.path.join(input_pdfs_dir, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)


            print("\n" + "="*50)
            continue_choice = input("ℕ Deseja realizar outra conversão? (s/n): ").strip().lower()

            if continue_choice != 's':
                print("👋 Programa finalizado!")
                break

        except KeyboardInterrupt:
            print("\n\n⚠️ Operação cancelada pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Ocorreu um erro inesperado: {str(e)}")
            continue
