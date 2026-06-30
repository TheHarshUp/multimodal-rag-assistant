from pypdf import PdfReader


def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for i, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text and page_text.strip():
            text += f"\n[PAGE {i}]\n"
            text += page_text + "\n"

    return text
