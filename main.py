import os
import warnings
import subprocess
import argparse # Adicionar argparse

# Ignorar warnings
warnings.filterwarnings('ignore')

# Importar funções auxiliares do utils.py
from utils import create_directories, display_menu, upload_pdfs, download_files, show_welcome

# Importar todas as funções de conversão do conversor.py
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
    pdf_to_csv_conversion # Importar a função movida
)

def install_dependencies():
    """Instala dependências do sistema e Python"""
    print("🔄 Instalando dependências do sistema...")
    subprocess.run(['apt-get', 'update', '-qq'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'poppler-utils', 'tesseract-ocr', 'tesseract-ocr-por'], check=True)
    print("✅ Dependências do sistema instaladas.")

    print("🔄 Instalando dependências Python via requirements.txt...")
    subprocess.run(['pip', 'install', '-q', '-r', 'requirements.txt'], check=True)
    print("✅ Dependências Python instaladas.")

def parse_arguments():
    """Configura e retorna o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Conversor de PDF modular para diversos formatos.")
    parser.add_argument(
        '-f', '--files',
        nargs='+',
        help='Um ou mais caminhos para os arquivos PDF de entrada.'
    )
    parser.add_argument(
        '-c', '--choice',
        type=int,
        choices=range(1, 14),
        help='Número da opção de conversão (1-13).' # 0 para sair é apenas interativo
    )
    return parser.parse_args()

def main_converter(args):
    """Função principal do conversor, adaptada para CLI e interativo."""

    print("🔄 Inicializando Conversor de PDF...")

    # Determinar modo de execução: CLI ou interativo
    is_cli_mode = args.files is not None and args.choice is not None

    if is_cli_mode:
        print("⚙️ Modo CLI ativado.")
        pdf_files_to_process = upload_pdfs(args.files)
        if not pdf_files_to_process:
            print("❌ Nenhum PDF válido fornecido via linha de comando. Encerrando.")
            return
        choice = str(args.choice)

        converted_files = []

        # Lógica de conversão para modo CLI
        if choice == '10': # Mesclar PDFs
            if len(pdf_files_to_process) < 2:
                print("⚠️ É necessário pelo menos 2 PDFs para mesclar no modo CLI. Encerrando.")
                return
            result = merge_pdfs(pdf_files_to_process)
            if result: converted_files.append(result)
        else:
            for pdf_file in pdf_files_to_process:
                print(f"\n📄 Processando: {os.path.basename(pdf_file)}")
                if choice == '1':
                    result = pdf_to_text(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '2':
                    result = pdf_to_word(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '3':
                    result = pdf_to_excel(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '4':
                    result = pdf_to_images(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '5':
                    result = pdf_to_html(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '6':
                    result = pdf_to_pdfa(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '7':
                    result = pdf_ocr(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '8':
                    result = extract_images_from_pdf(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '9':
                    results_csv = pdf_to_csv_conversion(pdf_file)
                    converted_files.extend(results_csv)
                elif choice == '11':
                    result = split_pdf(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '12':
                    result = compress_pdf(pdf_file)
                    if result: converted_files.append(result)
                elif choice == '13':
                    print("🔄 Convertendo para todos os formatos...")
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
                        print(f"  🔄 Convertendo para {name}...")
                        result = func(pdf_file)
                        if result: converted_files.append(result)
                    print("  🔄 Convertendo para CSV...")
                    results_csv = pdf_to_csv_conversion(pdf_file)
                    converted_files.extend(results_csv)

        if converted_files:
            print(f"\n✅ Total de {len(converted_files)} arquivo(s) convertido(s) com sucesso!")
            download_files(converted_files)
        else:
            print("❌ Nenhuma conversão foi concluída com sucesso.")
        return # Encerrar após a execução CLI

    else: # Modo interativo
        while True:
            display_menu()
            try:
                choice = input("\n🔢 Digite o número da opção desejada: ").strip()

                if choice == '0':
                    print("👋 Saindo do conversor...")
                    break

                pdf_files_to_process = []
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '12', '13']:
                    print("\n📤 Para upload interativo, selecione seus PDFs agora.")
                    pdf_files_to_process = upload_pdfs()
                elif choice == '10': # Mesclar PDFs
                    print("\n📤 Para mesclar PDFs, selecione pelo menos 2 arquivos.")
                    pdf_files_to_process = upload_pdfs()
                    if len(pdf_files_to_process) < 2:
                        print("⚠️ É necessário selecionar pelo menos 2 PDFs para mesclar.")
                        continue
                else:
                    print("❌ Opção inválida! Por favor, escolha uma opção do menu.")
                    continue

                if not pdf_files_to_process:
                    print("⚠️ Nenhum PDF válido foi carregado.")
                    continue

                converted_files = []

                if choice == '10': # Special handling for merge_pdfs as it takes a list of files
                    result = merge_pdfs(pdf_files_to_process)
                    if result: converted_files.append(result)
                else:
                    # Processar cada arquivo PDF para as outras opções
                    for pdf_file in pdf_files_to_process:
                        print(f"\n📄 Processando: {os.path.basename(pdf_file)}")

                        if choice == '1':
                            result = pdf_to_text(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '2':
                            result = pdf_to_word(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '3':
                            result = pdf_to_excel(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '4':
                            result = pdf_to_images(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '5':
                            result = pdf_to_html(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '6':
                            result = pdf_to_pdfa(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '7':
                            result = pdf_ocr(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '8':
                            result = extract_images_from_pdf(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '9': # PDF to CSV
                            results_csv = pdf_to_csv_conversion(pdf_file)
                            converted_files.extend(results_csv)

                        elif choice == '11':
                            result = split_pdf(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '12':
                            result = compress_pdf(pdf_file)
                            if result: converted_files.append(result)

                        elif choice == '13':
                            print("🔄 Convertendo para todos os formatos...")
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
                                print(f"  🔄 Convertendo para {name}...")
                                result = func(pdf_file)
                                if result: converted_files.append(result)
                            print("  🔄 Convertendo para CSV...")
                            results_csv = pdf_to_csv_conversion(pdf_file)
                            converted_files.extend(results_csv)

                # Oferecer download dos arquivos convertidos
                if converted_files:
                    print(f"\n✅ Total de {len(converted_files)} arquivo(s) convertido(s) com sucesso!")

                    download_choice = input("📥 Deseja fazer download dos arquivos convertidos? (s/n): ").strip().lower()

                    if download_choice == 's':
                        download_files(converted_files)
                else:
                    print("❌ Nenhuma conversão foi concluída com sucesso.")

                # Limpar arquivos temporários
                print("\n🧹 Limpando arquivos temporários...")
                if os.path.exists("temp_files"): # Check if directory exists before iterating
                    for file in os.listdir("temp_files"):
                        os.remove(os.path.join("temp_files", file))

                print("\n" + "="*50)
                continue_choice = input("🔄 Deseja realizar outra conversão? (s/n): ").strip().lower()

                if continue_choice != 's':
                    print("👋 Programa finalizado!")
                    break

            except KeyboardInterrupt:
                print("\n\n⚠️ Operação cancelada pelo usuário.")
                break
            except Exception as e:
                print(f"\n❌ Ocorreu um erro: {str(e)}")
                continue

if __name__ == "__main__":
    # Instalar dependências
    install_dependencies()

    # Criar diretórios (garante que existem antes de qualquer operação)
    create_directories()

    args = parse_arguments()

    # Exibir mensagem de boas-vindas apenas em modo interativo
    if args.files is None and args.choice is None:
        show_welcome()

    # Executar conversor
    main_converter(args)

    print("\n🎉 Processo concluído!")
    print("📂 Os arquivos convertidos estão na pasta 'output_files/'")

print("✅ main.py atualizado com sucesso!")
