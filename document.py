import os
import logging
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    logging.warning("pypdf is not installed. PDF loading will not work. Install with: pip install pypdf")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    A lightweight, modular document loader for a simple RAG system.
    Provides functionality to load and extract text from PDF and TXT files.
    """

    def __init__(self):
        """Initialize the DocumentLoader."""
        pass

    def load_pdf(self, file_path: str) -> str:
        """
        Load a PDF file and extract its text.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            str: The extracted text from the PDF.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is empty or text cannot be extracted.
            Exception: For any other errors during PDF processing.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        extracted_text = []
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
        except Exception as e:
            logger.error(f"Failed to read PDF {file_path}. Error: {e}")
            raise

        final_text = "\n".join(extracted_text).strip()
        
        if not final_text:
            logger.error(f"PDF file is empty or contains no extractable text: {file_path}")
            raise ValueError(f"Empty or unreadable PDF: {file_path}")

        logger.info(f"Successfully loaded PDF: {file_path}")
        return final_text

    def load_txt(self, file_path: str) -> str:
        """
        Load a TXT file and return its textual content.

        Args:
            file_path (str): The path to the TXT file.

        Returns:
            str: The text content of the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is empty.
            Exception: For encoding or reading errors.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read TXT {file_path}. Error: {e}")
            raise

        if not extracted_text:
            logger.error(f"TXT file is empty: {file_path}")
            raise ValueError(f"Empty TXT file: {file_path}")

        logger.info(f"Successfully loaded TXT: {file_path}")
        return extracted_text

    def load_document(self, file_path: str) -> str:
        """
        Automatically detect the file format and load the document.
        Supported formats: .pdf, .txt.

        Args:
            file_path (str): The path to the document.

        Returns:
            str: The extracted text.

        Raises:
            ValueError: If the file format is not supported.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            return self.load_pdf(file_path)
        elif ext == '.txt':
            return self.load_txt(file_path)
        else:
            logger.error(f"Unsupported document format: {ext} for file {file_path}")
            raise ValueError(f"Unsupported format: '{ext}'. Supported formats are .pdf and .txt.")

if __name__ == "__main__":
    # Example Usage
    loader = DocumentLoader()

    # Create a temporary txt file for testing
    sample_txt_path = "sample.txt"
    try:
        if not os.path.exists(sample_txt_path):
            with open(sample_txt_path, "w", encoding="utf-8") as file:
                file.write("This is a sample document for testing the RAG Document Loader.")
        
        # Load the document
        text = loader.load_document(sample_txt_path)
        print("------------- Extracted Text -------------")
        print(text)
        print("------------------------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up the sample TXT file
        if os.path.exists(sample_txt_path):
            os.remove(sample_txt_path)
