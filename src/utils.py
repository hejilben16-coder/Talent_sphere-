import os
import shutil


def clear_vector_store(path="vector_store"):
    """Delete the existing vector database."""
    if os.path.exists(path):
        shutil.rmtree(path)


def format_file_size(size):
    """Convert bytes to KB/MB."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    else:
        return f"{size / (1024 * 1024):.2f} MB"


def is_pdf(filename):
    """Check if the uploaded file is a PDF."""
    return filename.lower().endswith(".pdf")