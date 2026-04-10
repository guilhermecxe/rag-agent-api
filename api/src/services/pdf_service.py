from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
import fitz


class PDFService:
    def __init__(self):
        pass

    def read(self, pdf_bytes: bytes, pdf_title: str) -> list[Document]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        documents = []
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            text = page.get_text()
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": page_number+1,
                        "title": pdf_title,
                        "type": "pdf"
                    })
            )
        return documents