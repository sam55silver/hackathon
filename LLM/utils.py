from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from typing import List, Optional
from tavily import TavilyClient
def get_doc_tools(
    file_path: str,
    name: str,
) -> str:
    """Get vector query and summary query tools from a document."""

    # load documents
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    
    def vector_query(
        query: str, 
        page_numbers: Optional[List[str]] = None
    ) -> str:
        """Use to answer questions over a given paper.
    
        Useful if you have specific questions over the paper.
        Always leave page_numbers as None UNLESS there is a specific page you want to search for.
    
        Args:
            query (str): the string query to be embedded.
            page_numbers (Optional[List[str]]): Filter by set of pages. Leave as NONE 
                if we want to perform a vector search
                over all pages. Otherwise, filter by the set of specified pages.
        
        """
    
        page_numbers = page_numbers or []
        metadata_dicts = [
            {"key": "page_label", "value": p} for p in page_numbers
        ]
        
        query_engine = vector_index.as_query_engine(
            similarity_top_k=2,
            filters=MetadataFilters.from_dicts(
                metadata_dicts,
                condition=FilterCondition.OR
            )
        )
        response = query_engine.query(query)
        return response
        
    
    vector_query_tool = FunctionTool.from_defaults(
        name=f"vector_tool_{name}",
        fn=vector_query
    )
    
    summary_index = SummaryIndex(nodes)
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    summary_tool = QueryEngineTool.from_defaults(
        name=f"summary_tool_{name}",
        query_engine=summary_query_engine,
        description=(
            f"Useful for summarization questions related to {name}"
        ),
    )

    return vector_query_tool, summary_tool

from llama_index.core.tools import FunctionTool

def search_research_papers(query: str, max_results: int = 10) -> list:
    """
    Searches for related research papers based on a given query using the Tavily search API.

    This function utilizes Tavily, a specialized research search tool, to locate relevant academic 
    papers, providing up to `max_results` papers that match the input `query`.

    Args:
        query (str): The search term or phrase to locate related research papers.
        max_results (int, optional): The maximum number of search results to return. Defaults to 10.

    Returns:
        list: A list of dictionaries containing information about the relevant research papers, 
        including titles, authors, abstracts, and links.

    Example:
        >>> search_research_papers("machine learning in healthcare", max_results=5)
        [{"title": "...", "authors": "...", "abstract": "...", "link": "..."}, ...]
    """
    client = TavilyClient(api_key="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")

    # Step 2. Executing a simple search query
    return client.search(query, max_results=max_results)




# from tavily import TavilyClient

# # Step 1. Instantiating your TavilyClient
# tavily_client = TavilyClient(api_key="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")

# # Step 2. Executing a context search query
# answer = tavily_client.qna_search(query="Who is Leo Messi?")

# # Step 3. That's it! You now have a context string that you can feed directly into your RAG Application
# print(answer) 