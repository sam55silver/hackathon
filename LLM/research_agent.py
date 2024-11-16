from utils import get_doc_tools
from pathlib import Path
import os
from tavily import TavilyClient
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner
from llama_index.core.tools import FunctionTool

papers = [
    r"C:\Users\NoahB\OneDrive\Desktop\LLMs\docs\animal2vec.pdf",
    r"C:\Users\NoahB\OneDrive\Desktop\LLMs\docs\metaGPT.pdf"
]

paper_to_tools_dict = {}
for paper in papers:
    print(f"Getting tools for paper: {paper}")
    vector_tool, summary_tool = get_doc_tools(paper, Path(paper).stem)
    paper_to_tools_dict[paper] = [vector_tool, summary_tool]
    
def tavily_search(query: str, max_results: int = 10) -> list:
    """
    
    Helps for searching for new information. 

    Args:
        query (str): The search term.
        max_results (int, optional): The maximum number of search results to return. Defaults to 10.

    Returns:
        list: A list of dictionaries containing information about the top n search results

    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # Step 2. Executing a simple search query
    return client.search(query, max_results=max_results)

tavily_search = FunctionTool.from_defaults(fn=tavily_search)

initial_tools = [t for paper in papers for t in paper_to_tools_dict[paper]]
initial_tools.append(tavily_search)

llm = OpenAI(model="gpt-3.5-turbo-0125")

agent_worker = FunctionCallingAgentWorker.from_tools(
    initial_tools, 
    llm=llm, 
    verbose=True
)
agent = AgentRunner(agent_worker)

response = agent.query(
    "Can you tell me how MetaGPT could be used to improve animal2vec"
    "Can you find the google scholar page for the first author of animal2vec?"
)
