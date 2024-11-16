"""
Agent which operates over document indexes plus additional tools

Tool 1: Enviro NS agent
A) build index for each doc in enviro NS
B) build tool retrieval over all of the different vector indexes

Tool 2: Planning Appl agent
A) build index for each doc in Planning Appl
B) build tool retrieval over all of the different vector indexes

If not enought information in docs is available provide naturalist tool to search further 
"""
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner
from llama_index.llms.openai import OpenAI


from utils import return_tools_from_index_store

def pdf_agent(index_dir, system_prompt, retriever_top_k=3):
    
    tools = return_tools_from_index_store(index_dir)
    llm = OpenAI(model="gpt-3.5-turbo")
    
    obj_index = ObjectIndex.from_objects(
    tools,
    index_cls=VectorStoreIndex,
    )
    obj_retriever = obj_index.as_retriever(similarity_top_k=retriever_top_k)
    agent_worker = FunctionCallingAgentWorker.from_tools(
    tool_retriever=obj_retriever,
    llm=llm, 
    system_prompt=system_prompt,
        verbose=True
    )
    
    return AgentRunner(agent_worker)
    
enviro_agent = pdf_agent(index_dir="C:/Users/NoahB/hackathon/data/indexes/enviro_ns",
                            system_prompt= """ \
                            You are an agent designed to answer queries over a set of given papers.
                            Please always use the tools provided to answer a question. Do not rely on prior knowledge./

                            """,
                            retriever_top_k=3)


response = enviro_agent.query(
    "Tell me about atlantic coastal plain flora ammendment "
    "and find a document about a similar area."
)
print(str(response))