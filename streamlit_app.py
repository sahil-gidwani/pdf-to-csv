import streamlit as st
import pandas as pd
import pdfplumber  # For PDF handling
import time
import gc  # For memory management

# Function to extract table data from PDF without repeating headers
def extract_table_from_pdf(pdf_file):
    first_page = True
    header = None

    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            progress_bar = st.progress(0)

            for i, page in enumerate(pdf.pages):
                progress = (i + 1) / total_pages
                progress_bar.progress(progress)

                table = page.extract_table()
                if table:
                    if first_page:
                        # Take the header from the first page
                        header = table[0]
                        # Skip the header row in the first page
                        yield table[1:], header
                        first_page = False
                    else:
                        # Skip the header row in subsequent pages
                        yield table[1:], None

                # Free up memory from the processed page
                del page
                gc.collect()

            # Complete the progress bar
            time.sleep(0.1)
            progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
        return None

# Convert extracted table into a DataFrame incrementally
def append_to_dataframe(df, data_chunk, header):
    try:
        # Create a DataFrame for the current chunk of table data
        df_chunk = pd.DataFrame(data_chunk, columns=header if header else df.columns)
        # Append to the main DataFrame
        df = pd.concat([df, df_chunk], ignore_index=True)
        return df
    except Exception as e:
        st.error(f"An error occurred while converting to DataFrame: {e}")
        return df

# Streamlit app interface
st.title('📄 PDF to CSV Converter 📊')

st.write("This app extracts tabular data from PDFs and converts them into CSV format. Upload a PDF file to get started.")

uploaded_file = st.file_uploader("📁 Upload a PDF file", type="pdf")

if uploaded_file is not None:
    st.info("Extracting data from the PDF, please wait...")

    # Initialize an empty DataFrame
    df = pd.DataFrame()

    # Extract table from uploaded PDF in chunks
    table_generator = extract_table_from_pdf(uploaded_file)

    try:
        for table_data, header in table_generator:
            # Append each table chunk to the main DataFrame
            df = append_to_dataframe(df, table_data, header)
            # Free up memory for the current chunk
            gc.collect()

        if not df.empty:
            st.write("✅ Data extraction complete!")
            st.write(df)

            # Allow user to download CSV
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
