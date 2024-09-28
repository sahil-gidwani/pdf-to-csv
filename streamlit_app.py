import streamlit as st
import pandas as pd
import pdfplumber  # For PDF handling
import time

# Function to extract table data from PDF without repeating headers


def extract_table_from_pdf(pdf_file):
    tables = []
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
                        tables.extend(table[1:])
                        first_page = False
                    else:
                        # Just take the data from the subsequent pages (ignore header)
                        # Skip the header row in subsequent pages
                        tables.extend(table[1:])

            # Complete the progress bar
            time.sleep(0.1)
            progress_bar.empty()

    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
        return None, None

    if not tables:
        st.warning("No tables were found in the PDF.")
        return None, None

    return header, tables

# Convert extracted table into a DataFrame


def convert_to_dataframe(header, table):
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
            st.write(df.head(10))

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
        st.warning(
            "No valid data extracted from the PDF. Please check the file format.")

else:
    st.warning("Please upload a PDF file to continue.")
