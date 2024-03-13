# PDF-GPT4-JSON

This project is designed to convert PDF files into JSON format using GPT-4. For each page in the PDF, a JSON file will be generated. The hierarchy of the JSON structure will be inferred from the layout of the data in the PDF.

## Theory of Generating Structured JSON using GPT-4 Vision

GPT-4 Vision is a state-of-the-art language model that has been fine-tuned for image understanding and analysis. It leverages the power of deep learning to extract meaningful information from PDF files and convert them into structured JSON format.

The process of generating structured JSON using GPT-4 Vision involves the following steps:

1. **PDF Parsing**: The PDF file is parsed to extract the textual content and layout information of each page.

2. **Text Extraction**: The extracted text is processed to remove any noise or irrelevant information, such as headers, footers, and page numbers.

3. **Layout Analysis**: GPT-4 Vision analyzes the layout of the text on each page to identify the hierarchical structure of the data. It looks for patterns, indentation, and formatting cues to infer the relationships between different elements.

4. **JSON Generation**: Based on the layout analysis, GPT-4 Vision generates a structured JSON representation of the PDF content. Each page is represented as a separate JSON file, with nested objects and arrays to capture the hierarchical relationships.

By leveraging the power of GPT-4 Vision, the PDF-GPT4-JSON project simplifies the process of converting PDF files into structured JSON format. This enables developers to easily extract and analyze data from PDFs, opening up a wide range of possibilities for data processing and automation.


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/PDF-GPT4-JSON.git
    ```
2. Navigate to the project directory:

    ```bash
    cd PDF-GPT4-JSON
    ```
3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt

## Usage
1. OPENAI Key

    Supply your Open AI key as an Enviroment variable `OPENAI_API_KEY`  or  as a command line argument  `--openai-key`

 

2. Run the conversion script:

    ```bash
    python main.py ../samples/sample.pdf 
    ```

    Will generate tmp working folder and an output folder with json for each page.

## Contributing

Contributions are welcome! Please follow the guidelines in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [GLP-3 LICENSE](LICENSE).