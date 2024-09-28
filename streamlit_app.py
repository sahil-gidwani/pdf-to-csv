import streamlit as st
import pandas as pd
import pdfplumber  # For PDF handling
import time


def extract_table_from_pdf(pdf_file):
    """
    Extracts tables from a PDF file, ignoring repeated headers on subsequent pages.

    Args:
        pdf_file: Uploaded PDF file.

    Returns:
        header: List of column headers.
        tables: List of table rows extracted from the PDF.
    """
    tables = []
    first_page = True
    header = None

    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            progress_bar = st.progress(0)

            # Loop through each page of the PDF and extract tables
            for i, page in enumerate(pdf.pages):
                # st.info(f"Processing page {i + 1} of {total_pages}...")
                progress = (i + 1) / total_pages
                update_progress_bar(progress_bar, progress)

                first_page, header, tables = process_pdf_page(page, first_page, tables, header)

            # Complete the progress bar
            progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}. "
                 f"Please ensure the file is a valid PDF and try again.")
        return None, None

    if not tables:
        st.warning("No tables were found in the PDF.")
        return None, None

    return header, tables


def process_pdf_page(page, first_page, tables, header):
    """
    Processes a single PDF page and extracts the table from it.

    Args:
        page: A single page object from the PDF.
        first_page: Boolean indicating if it’s the first page.
        tables: List to store table data from all pages.
        header: The table header to store only from the first page.

    Returns:
        first_page: Updated boolean indicating whether it’s still the first page.
        header: Table header (from the first page).
        tables: Updated table data with rows extracted from the page.
    """
    table = page.extract_table()

    if table:
        if first_page:
            # Take the header from the first page
            header = table[0]
            # Skip the header row in the first page
            tables.extend(table[1:])
            first_page = False
        else:
            # Skip the header row in subsequent pages
            tables.extend(table[1:])

    return first_page, header, tables


def update_progress_bar(progress_bar, progress):
    """
    Updates the progress bar in Streamlit.

    Args:
        progress_bar: Streamlit progress bar object.
        progress: Progress value between 0 and 1.
    """
    progress_bar.progress(progress)


def convert_to_dataframe(header, table):
    """
    Converts extracted table data into a pandas DataFrame.

    Args:
        header: Column headers for the DataFrame.
        table: Data extracted from the PDF.

    Returns:
        df: DataFrame containing the extracted table data.
    """
    try:
        df = pd.DataFrame(table, columns=header)
        return df
    except Exception as e:
        st.error(f"An error occurred while converting to DataFrame: {e}")
        return None


# Streamlit app interface
st.title('📄 PDF to CSV Converter 📊')

st.write("This app extracts tabular data from PDFs and converts them into CSV format. Upload a PDF file to get started.")

uploaded_file = st.file_uploader("📁 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting data from the PDF, please wait...")

    # Extract table from uploaded PDF
    header, table_data = extract_table_from_pdf(uploaded_file)

    if header and table_data:
        df = convert_to_dataframe(header, table_data)

        if df is not None:
            st.write("✅ Data extraction complete!")
            st.write(df.head(10))  # Display the first 10 rows of the extracted data

            # Allow user to download the extracted data as a CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name='extracted_data.csv',
                mime='text/csv'
            )
            st.success("CSV file is ready for download!")
    else:
        st.warning("No valid data extracted from the PDF. Please check the file format.")

else:
    st.warning("Please upload a PDF file to continue.")
