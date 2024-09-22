# 📄 PDF to CSV Converter 📊

This Streamlit app extracts tabular data from PDFs and converts them into CSV format. Upload a PDF file to get started.

## Features

- Extracts tables from PDF files
- Converts extracted tables into a Pandas DataFrame
- Allows downloading the extracted data as a CSV file

## Installation

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```sh
     .\venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:

   ```sh
   streamlit run streamlit_app.py
   ```

2. Open your web browser and go to `http://localhost:8501`.

3. Upload a PDF file to extract tabular data and download it as a CSV file.
