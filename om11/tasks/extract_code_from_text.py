import re

def extract_code_from_text(text):
    match = re.search(r'\b\d{6}\b', text)
    return match.group(0) if match else "Код не найден"