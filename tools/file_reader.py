import os
import structlog
from typing import Optional

logger = structlog.get_logger()

class FileReaderTool:
    """
    Reads content from local files (PDF, TXT, MD).
    """

    def read_file(self, file_path: str) -> Optional[str]:
        """
        Reads a file and returns its text content.
        Supports: .txt, .md, .pdf
        """
        file_path = file_path.strip().strip('"').strip("'") # Clean path
        
        if not os.path.exists(file_path):
            logger.warning("file_not_found", path=file_path)
            # Check if it's a relative path?
            if os.path.exists(os.path.join(os.getcwd(), file_path)):
                 file_path = os.path.join(os.getcwd(), file_path)
            else:
                 return None

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".pdf":
                return self._read_pdf(file_path)
            elif ext in [".txt", ".md", ".log", ".py"]:
                return self._read_text(file_path)
            else:
                logger.warning("unsupported_extension", ext=ext)
                return None
        except Exception as e:
            logger.error("read_file_error", error=str(e), path=file_path)
            return None

    def _read_text(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_pdf(self, path: str) -> str:
        text = ""
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            for page in reader.pages:
                t = page.extract_text()
                if t: text += t + "\n"
        except ImportError:
            # Fallback or error
            logger.error("pypdf_missing", msg="Install pypdf to read PDF files.")
            return "Error: pypdf not installed."
        return text

