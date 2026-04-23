from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
import fitz


class PDFService:
    """Serviço de extração de texto de arquivos PDF.

    Usa PyMuPDF (fitz) para abrir PDFs em memória e extrair o conteúdo
    de cada página como um Document LangChain.
    """

    def __init__(self):
        pass

    def read(self, pdf_bytes: bytes, pdf_title: str) -> list[Document]:
        """Extrai o texto de cada página de um PDF e o converte em Documents.

        Args:
            pdf_bytes (bytes): Conteúdo binário do arquivo PDF.
            pdf_title (str): Título usado nos metadados de cada Document gerado.

        Returns:
            list[Document]: Lista com um Document por página, contendo:
                - ``page_content``: Texto extraído da página.
                - ``metadata.page``: Número da página (base 1).
                - ``metadata.title``: Título do arquivo.
                - ``metadata.type``: Sempre ``"pdf"``.
        """
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