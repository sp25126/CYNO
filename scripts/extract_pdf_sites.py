import pdfplumber
import re

pdf_path = r"c:/Users/saumy/OneDrive/Desktop/job/Remote Jobs.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Simple regex to find domains roughly
    domains = re.findall(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}', text)
    unique_domains = sorted(list(set(domains)))
    
    print("Found Sites:")
    for d in unique_domains:
        print(d)

except Exception as e:
    print(f"Error reading PDF: {e}")
