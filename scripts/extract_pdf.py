from pypdf import PdfReader
import sys

try:
    reader = PdfReader(r"c:\Users\saumy\OneDrive\Desktop\job\Remote Jobs.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    print(text)
except Exception as e:
    print(f"Error reading PDF: {e}")
