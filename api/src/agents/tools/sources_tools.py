from langchain_core.tools import StructuredTool

from src.services.sources_service import SourcesService


class SourcesToolkit:
    def __init__(self, sources_service: SourcesService):
        self._sources_service = sources_service

    def _get_sources(self, page: int = 1) -> dict:
        """Retorna uma lista paginada das fontes disponíveis na base de conhecimento.

        Args:
            page: Número da página a ser retornada. O índice começa em 1. Padrão: 1.

        Returns:
            Dicionário contendo as fontes disponíveis da página requisitada,
            incluindo o número da página e o número da última página disponível.
        """
        sources = self._sources_service.get_sources(page=page)
        return sources
    
    def _search_sources_regex(self, pattern: str, page: int = 1) -> dict:
        """Busca fontes cujo nome corresponde a um padrão de expressão regular.

        Use esta ferramenta quando precisar encontrar fontes específicas pelo nome,
        utilizando padrões regex para correspondências parciais ou flexíveis.

        Args:
            pattern: Expressão regular usada para filtrar os nomes das fontes.
                Exemplo: ``"relatorio_2024.*"`` para fontes cujo nome começa com
                ``relatorio_2024``.
            page: Número da página a ser retornada. O índice começa em 1. Padrão: 1.

        Returns:
            Dicionário contendo as fontes cujos nomes correspondem ao padrão,
            incluindo o número da página e o número da última página disponível.
        """
        sources = self._sources_service.search_sources_regex(pattern=pattern, page=page)
        return sources
    
    def _search_excerpts_regex(self, pattern: str, sources: list[str] | None = None, page: int = 1) -> dict:
        """Busca trechos de documentos cujo conteúdo corresponde a um padrão de expressão regular.

        Use esta ferramenta para localizar trechos relevantes dentro das fontes indexadas.
        Opcionalmente, restrinja a busca a um subconjunto de fontes para maior precisão.
        Os resultados incluem o índice de cada trecho, que pode ser usado com
        ``_get_excerpt`` para recuperar trechos vizinhos.

        Args:
            pattern: Expressão regular usada para filtrar o conteúdo dos trechos.
                Exemplo: ``"taxa de juros"`` para trechos que mencionam esse termo.
            sources: Lista de nomes de fontes nas quais a busca será restringida.
                Se ``None``, a busca abrange todas as fontes disponíveis. Padrão: None.
            page: Número da página a ser retornada. O índice começa em 1. Padrão: 1.

        Returns:
            Lista de dicionários, cada um contendo ``source`` (nome da fonte),
            ``index`` (posição do trecho na fonte) e ``excerpt`` (conteúdo do trecho).
        """
        excerpts = self._sources_service.search_excerpts_regex(
            pattern=pattern,
            sources=sources,
            page=page
        )

        results = [{
            "source": excerpt.metadata["title"],
            "index": excerpt.metadata["index"],
            "excerpt": excerpt.page_content
        } for excerpt in excerpts["relevant_excerpts"]]
        
        return {
            "excerpts": results,
            "current_page": excerpts["current_page"],
            "last_page": excerpts["last_page"],
        }
    
    def _search_excerpts_semantic(self, query: str, sources: list[str] | None = None) -> list[dict]:
        """Busca trechos de documentos semanticamente similares à query.

        Prefira esta ferramenta a ``_search_excerpts_regex`` quando a intenção de busca
        for expressa em linguagem natural, pois ela utiliza similaridade de embeddings
        para encontrar trechos relevantes mesmo sem correspondência exata de termos.
        Os resultados incluem o índice de cada trecho, que pode ser usado com
        ``_get_excerpt`` para recuperar trechos vizinhos.

        Args:
            query: Texto em linguagem natural descrevendo o que se deseja encontrar.
                Exemplo: ``"impacto da inflação nos investimentos de renda fixa"``.
            sources: Lista de nomes de fontes nas quais a busca será restringida.
                Se ``None``, a busca abrange todas as fontes disponíveis. Padrão: None.

        Returns:
            Lista de dicionários, cada um contendo ``source`` (nome da fonte),
            ``index`` (posição do trecho na fonte) e ``excerpt`` (conteúdo do trecho).
        """
        excerpts = self._sources_service.search_excerpts_semantic(
            query=query,
            source_names=sources,
        )

        return [{
            "source": excerpt.metadata["title"],
            "index": excerpt.metadata["index"],
            "excerpt": excerpt.page_content,
        } for excerpt in excerpts]

    def _get_excerpt(self, source_name: str, index: int) -> str:
        """Recupera o conteúdo de um trecho específico de uma fonte.

        É útil para recuperar trechos vizinhos ao incrementar ou decrementar o índice.

        Args:
            source_name: Nome exato da fonte à qual o trecho pertence.
            index: Posição do trecho dentro da fonte.

        Returns:
            Dicionário contendo ``source`` (nome da fonte), ``index`` (posição do trecho)
            e ``excerpt`` (conteúdo completo do trecho).
        """
        excerpt = self._sources_service.get_excerpt(
            source_name=source_name,
            index=index
        )

        return {
            "source": source_name,
            "index": index,
            "excerpt": excerpt.page_content
        }
    
    def get_tools(self) -> list[StructuredTool]:
        return [
            StructuredTool.from_function(self._get_sources),
            StructuredTool.from_function(self._search_sources_regex),
            StructuredTool.from_function(self._search_excerpts_regex),
            StructuredTool.from_function(self._search_excerpts_semantic),
            StructuredTool.from_function(self._get_excerpt),
        ]
