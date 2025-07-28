import os
import json
from utils import extract_outline

INPUT_DIR = '/app/input'
OUTPUT_DIR = '/app/output'

def main():
    for fname in os.listdir(INPUT_DIR):
        if fname.lower().endswith('.pdf'):
            pdf_path = os.path.join(INPUT_DIR, fname)
            outline = extract_outline(pdf_path)
            out_name = fname.rsplit('.',1)[0]+'.json'
            with open(os.path.join(OUTPUT_DIR, out_name), 'w', encoding='utf-8') as f:
                json.dump(outline, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
