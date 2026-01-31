# 📄 Conversor de PDF Modular

Este projeto é um conversor de arquivos PDF versátil e modularizado. Ele permite realizar diversas operações em PDFs, como conversão para múltiplos formatos (texto, Word, Excel, imagens, HTML, PDF/A, CSV), aplicação de OCR, extração de imagens, mesclagem, divisão e compressão de PDFs.

## Funcionalidades

- **PDF para Texto (.txt)**: Extrai todo o conteúdo textual de um PDF.
- **PDF para Word (.docx)**: Converte PDFs em documentos editáveis do Word.
- **PDF para Excel (.xlsx)**: Extrai tabelas de PDFs para planilhas Excel.
- **PDF para Imagens (.jpg/.png)**: Converte cada página do PDF em uma imagem.
- **PDF para HTML**: Transforma o conteúdo do PDF em um arquivo HTML simples.
- **PDF para PDF/A**: Converte PDFs para o formato arquivável PDF/A.
- **PDF com OCR**: Aplica Reconhecimento Ótico de Caracteres para tornar PDFs pesquisáveis.
- **Extrair Imagens do PDF**: Salva todas as imagens incorporadas em um PDF.
- **PDF para CSV**: Extrai tabelas de PDFs para arquivos CSV.
- **Mesclar Múltiplos PDFs**: Combina vários PDFs em um único documento.
- **Dividir PDF por Páginas**: Separa um PDF em arquivos individuais por página.
- **Comprimir PDF**: Reduz o tamanho do arquivo do PDF.
- **Converter Todas as Opções**: Realiza múltiplas conversões simultaneamente.

## Estrutura do Projeto

O projeto é modularizado para facilitar a manutenção e a expansão:

- `main.py`: Contém a lógica principal do programa, incluindo a instalação de dependências, e a função `main_converter` que gerencia o fluxo do usuário em modo CLI. Também é o ponto de entrada principal para a execução do conversor em modo interativo via terminal.
- `utils.py`: Armazena funções utilitárias e auxiliares, como `create_directories` (para configurar a estrutura de pastas), `display_menu` (para exibir as opções ao usuário no modo CLI/interativo), `upload_pdfs` (para gerenciar o upload de arquivos via CLI ou web) e `download_files` (para compactar e disponibilizar os resultados).
- `conversor.py`: Concentra todas as funções específicas de conversão de PDF. Cada função aqui é responsável por uma única operação de conversão (ex: `pdf_to_text`, `pdf_to_word`, `merge_pdfs`, etc.), garantindo a separação de responsabilidades.
- `web_converter/app.py`: O backend da aplicação web, construído com Flask. Lida com o upload de arquivos, chama as funções de conversão e gerencia o download dos resultados via HTTP.
- `web_converter/templates/index.html`: O frontend da aplicação web, que provê a interface gráfica para os usuários interagirem com o conversor.
- `requirements.txt`: Lista todas as bibliotecas Python necessárias para o projeto, facilitando a instalação do ambiente.
- `.gitignore`: Define quais arquivos e diretórios devem ser ignorados pelo controle de versão (Git), como arquivos de saída, temporários e caches.

## Instalação

Para configurar e executar o projeto, siga os passos abaixo:

1.  **Clone o repositório** ou faça download dos arquivos para o seu ambiente.

    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <nome_do_repositorio>
    ```

2.  **Instale as dependências do sistema e Python**:

    A execução do `main.py` em modo CLI ou interativo cuidará da instalação das dependências. No entanto, para o servidor web, você pode precisar instalar o `Flask` explicitamente, se não estiver no `requirements.txt` ou se preferir gerenciar separadamente.

    Para um ambiente local (não Colab) ou se preferir instalar manualmente:

    ```bash
    # Para sistemas Debian/Ubuntu (dependências do sistema para OCR e conversão):
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-por

    # Para todas as plataformas (dependências Python):
    pip install -r requirements.txt
    ```

## Como Usar

O conversor pode ser usado de três maneiras: **interativa** (via menu no terminal), **linha de comando (CLI)** ou **interface web**.

### Modo Interativo (Terminal)

1.  **Execute o script principal sem argumentos**:

    ```bash
    python main.py
    ```

    O programa exibirá um menu de opções. Escolha o número correspondente à conversão desejada e siga as instruções para upload/download.

### Modo Linha de Comando (CLI)

You pode executar conversões diretamente do terminal, fornecendo os arquivos de entrada e a opção de conversão como argumentos. Use `-h` ou `--help` para ver todas as opções:

```bash
python main.py --help
```

**Exemplos de Uso CLI:**

-   **Converter um PDF para Texto (Opção 1)**:

    ```bash
    python main.py -f caminho/para/meu_documento.pdf -c 1
    ```

-   **Mesclar vários PDFs (Opção 10)**:

    ```bash
    python main.py -f pdf_parte1.pdf pdf_parte2.pdf pdf_parte3.pdf -c 10
    ```
    *Nota: Para mesclar, forneça todos os PDFs a serem mesclados como `--files` e use a opção `-c 10`.*

### Modo Interface Web (Flask)

Para usar a interface web, você precisa iniciar o servidor Flask:

1.  **Navegue até o diretório `web_converter`**:

    ```bash
    cd web_converter
    ```

2.  **Inicie o servidor Flask**:

    ```bash
    python app.py
    ```

    Você verá uma mensagem indicando que o servidor está rodando, geralmente em `http://127.0.0.1:5000/`.

3.  **Acesse a interface no seu navegador**: Abra seu navegador e navegue até o endereço fornecido (ex: `http://127.0.0.1:5000/`).

4.  **Utilize a interface web**:
    -   **Selecione o Formato**: Clique em um dos cards de formato (ex: `DOCX`, `TXT`, `XLSX`) para escolher o tipo de conversão desejado.
    -   **Faça o Upload do PDF**: Arraste e solte seu arquivo PDF na área de upload ou clique nela para abrir o seletor de arquivos. (Para a opção "Mesclar PDFs", selecione múltiplos arquivos.)
    -   **Inicie a Conversão**: Clique no botão "PROCESSAR".
    -   **Baixe o Resultado**: Após a conclusão, um botão "BAIXAR" aparecerá para você fazer o download do arquivo ZIP contendo os resultados da conversão.

## Para Usuários Windows: Experiência de 'Clicar no Ícone'

Para uma experiência mais amigável no Windows, você pode:

### 1. Criar um Executável (para a versão CLI)

Você pode usar o `PyInstaller` para empacotar a versão CLI do seu conversor em um único arquivo `.exe`, eliminando a necessidade de instalar Python no ambiente de uso.

1.  **Instale PyInstaller** (se ainda não o fez):

    ```bash
    pip install pyinstaller
    ```

2.  **Gere o executável**:

    Navegue até o diretório raiz do projeto (`<nome_do_repositorio>`) no terminal e execute:

    ```bash
    pyinstaller --onefile main.py
    ```
    Isso criará uma pasta `dist` no diretório do seu projeto. Dentro dela, você encontrará `main.exe`.

3.  **Crie um Atalho no Desktop para a Versão CLI**:
    -   Localize o arquivo `main.exe` na pasta `dist`.
    -   Clique com o botão direito nele e selecione "Enviar para" > "Área de trabalho (criar atalho)".
    -   Você pode renomear o atalho (ex: "Conversor PDF CLI").
    -   Para usar, arraste e solte um arquivo PDF sobre o atalho ou execute-o e use-o via linha de comando no `cmd` que será aberto.

### 2. Iniciar a Aplicação Web com um Script (.bat)

O arquivo `start_web_converter.bat` já está configurado para iniciar o servidor Flask e abrir o navegador automaticamente. Para usá-lo facilmente:

1.  **Crie um Atalho no Desktop para a Versão Web**:
    -   Localize o arquivo `start_web_converter.bat` no diretório raiz do projeto.
    -   Clique com o botão direito nele e selecione "Enviar para" > "Área de trabalho (criar atalho)".
    -   Você pode renomear o atalho (ex: "Conversor PDF Web").
    -   Ao clicar duas vezes neste atalho, o servidor web será iniciado em segundo plano e a interface web será aberta no seu navegador padrão.

## Compatibilidade com Google Colab

Este projeto foi inicialmente desenvolvido para o Google Colab e é totalmente compatível. O modo interativo com suas funções de upload e download (`google.colab.files`) ainda é otimizado para este ambiente, proporcionando uma experiência fluida para usuários do Colab. No entanto, o projeto foi refatorado para ser uma aplicação Python genérica que pode ser executada em qualquer terminal com Python instalado (modo CLI) e também como uma aplicação web com Flask.
