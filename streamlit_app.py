import streamlit as st
import pandas as pd
import pdfplumber  # For PDF handling
import time
import gc  # For memory management

# Caching the table extraction to avoid redundant computation
@st.experimental_memo
def extract_table_from_pdf_cached(pdf_file):
    return list(extract_table_from_pdf_chunked(pdf_file))

# Function to extract table data from PDF in chunks without repeating headers
def extract_table_from_pdf_chunked(pdf_file):
    first_page = True
    header = None

    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            progress_bar = st.progress(0)

            # Chunk the PDF pages (e.g., 10 pages per chunk)
            chunk_size = 10
            for i in range(0, total_pages, chunk_size):
                chunk_pages = pdf.pages[i:i+chunk_size]

                for page in chunk_pages:
                    table = page.extract_table()
                    if table:
                        if first_page:
                            # Take the header from the first page
                            header = table[0]
                            # Yield table data without header
                            yield table[1:], header
                            first_page = False
                        else:
                            # Yield table data without repeating the header
                            yield table[1:], None

                    # Free up memory for the current page
                    del page

                # Force memory clean-up after processing the chunk
                gc.collect()

                # Update progress bar
                progress = (i + chunk_size) / total_pages
                progress_bar.progress(min(progress, 1.0))

            # Complete the progress bar
            time.sleep(0.1)
            progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
        return None

# Function to append chunks of table data to a DataFrame incrementally
def append_to_dataframe(df, data_chunk, header):
    try:
        # Create a DataFrame for the current chunk of table data
        df_chunk = pd.DataFrame(data_chunk, columns=header if header else df.columns)
        # Append the current chunk to the main DataFrame
        df = pd.concat([df, df_chunk], ignore_index=True)
        return df
    except Exception as e:
        st.error(f"An error occurred while converting to DataFrame: {e}")
        return df

# Streamlit app interface
st.title('📄 PDF to CSV Converter 📊')

st.write("This app extracts tabular data from PDFs and converts them into CSV format. Upload a PDF file to get started.")

# File uploader for PDF files
uploaded_file = st.file_uploader("📁 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting data from the PDF, please wait...")

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Extract table data from the uploaded PDF in chunks, using caching to optimize processing
    table_generator = extract_table_from_pdf_cached(uploaded_file)

    try:
        # Process each table chunk and append it to the DataFrame
        for table_data, header in table_generator:
            # Append each table chunk to the main DataFrame
            df = append_to_dataframe(df, table_data, header)
            # Explicitly manage memory after each chunk
            gc.collect()

        if not df.empty:
            st.write("✅ Data extraction complete!")
            st.write(df)

            # Allow the user to download the extracted data as a CSV
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
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

else:
    st.warning("Please upload a PDF file to continue.")
