from pathlib import Path
from pypdf import PdfReader

UPLOAD_FOLDER = Path("uploaded_pdfs")
UPLOAD_FOLDER.mkdir(exist_ok=True)


def save_uploaded_files(uploaded_files):
    """
    Save uploaded PDF files to disk.
    Returns a list of saved file paths.
    """

    saved_files = []

    for uploaded_file in uploaded_files:

        file_path = UPLOAD_FOLDER / uploaded_file.name

        if not file_path.exists():
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        saved_files.append(file_path)

    return saved_files


def load_pdfs(pdf_paths):
    """
    Load PDF files from disk and extract text.
    """

    documents = []

    for pdf_path in pdf_paths:

        reader = PdfReader(str(pdf_path))

        for page_num, page in enumerate(reader.pages, start=1):

            text = page.extract_text()

            if text:

                documents.append(
                    {
                        "source": pdf_path.name,
                        "page": page_num,
                        "text": text,
                    }
                )

    return documents