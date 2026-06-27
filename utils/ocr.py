import easyocr
#from pdf2image import convert_from_path

reader = None

def extract_text_with_ocr(pdf_path):
    global reader

    if reader is None:
        reader = easyocr.Reader(['en'], gpu=True)

    pages = convert_from_path(pdf_path)
    full_text = ""

    for page in pages:
        results = reader.readtext(page)
        page_text = " ".join([result[1] for result in results])
        full_text += page_text + "\n"

    return full_text