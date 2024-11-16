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
from llama_index.core.agent import AgentRunner
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import (
    FunctionCallingAgentWorker,
)
from llama_index.core.agent import ReActAgent

from .utils import return_tools_from_index_store

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

def general_agent():
    
    enviro_agent = pdf_agent(index_dir="./data/indexes/enviro_ns",
                                system_prompt= """ \
                                You are an agent designed to answer queries over a set of given papers.
                                Please always use the tools provided to answer a question. Do not rely on prior knowledge./

                                """,
                                retriever_top_k=3)

    planner_agent = pdf_agent(index_dir="./data/indexes/planning_app",
                                system_prompt= """ \
                                You are an agent designed to answer queries over a set of given papers.
                                Please always use the tools provided to answer a question. Do not rely on prior knowledge./

                                """,
                                retriever_top_k=3)
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=enviro_agent,
            metadata=ToolMetadata(
                name="enviro_agent", description="Agent that has information related to the environment."
            ),
        ),
        QueryEngineTool(
            query_engine=planner_agent,
            metadata=ToolMetadata(
                name="planner_agent",
                description="Agent that has information related to planning.",
            ),
        ),
    ]
    llm = OpenAI(model="gpt-3.5-turbo")
    outer_agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True)
    return outer_agent

agent = general_agent()
response = agent.query("can you tell me about atlantic coastal plain flora ammendment."
                       "can you share the page number where this is explained")

print(str(response))