import easyocr
import torch
import numpy as np
from pdf2image import convert_from_path

reader = None

def extract_text_with_ocr(pdf_path):
    global reader

    if reader is None:
        use_gpu = torch.cuda.is_available()
        reader = easyocr.Reader(['en'], gpu=use_gpu)

    pages = convert_from_path(pdf_path, dpi=200)

    page_results = []

    for page_num, page in enumerate(pages, start=1):
        page_np = np.array(page)

        results = reader.readtext(page_np, paragraph=True)

        page_text = " ".join([r[1] for r in results])

        page_results.append({
            "page": page_num,
            "text": page_text
        })

    return page_results