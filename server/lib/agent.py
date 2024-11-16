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
import os
from typing import Optional, List
from .utils import return_tools_from_index_store, build_global_planner_tools
from .utils import return_tools_from_index_store

from .perplexica import search_internet_tool

def build_agent(tools, system_prompt, retriever_top_k=3):
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
    
def pdf_agent(index_dir, system_prompt, retriever_top_k=3):
    tools = return_tools_from_index_store(index_dir)
    return build_agent(tools, system_prompt, retriever_top_k=retriever_top_k)

def global_planner_agent(system_prompt, retriever_top_k=3):
    tools = build_global_planner_tools()
    return build_agent(tools, system_prompt, retriever_top_k=retriever_top_k)
    
    
def general_agent():
    
    enviro_agent = pdf_agent(index_dir="./data/indexes/enviro_ns",
                                system_prompt=f""" /
                                ### Role
                                You are an environmental consultant providing expert advice to a project developer on the environmental impact of their proposed project. 
                                ### Task
                                Your step 1 task is to identify ecosystems and habitats that might be present at the specific user inputted project location, focusing on the precise area. 
                                Your step 2 task, is to cross reference the ecosystems and habitats identified in step 1 against your  specialised knowledge base of reference material to identify at risk habitats, flora and fauna that may be present in the location along with any regulations, laws or conservation efforts in place for the flora and fauna occurrences. 
                                Your step 3 task, is to present the identified step 2 flora and fauna, referring the associated step 1 ecosystem associated with each identified flora and fauna item. 
                                ### Information handling
                                For step 1 you are to use general information. 
                                For step 2 You will be provided with relevant extracts from a knowledge base. Use this information to answer questions and complete the task. Prioritize the most relevant information. If there are conflicting details, try to reconcile them or explain the discrepancies. If the provided information is insufficient, state that clearly and avoid making assumptions.
                                ### Tone
                                A professional factual tone is to be used throughout. 
                                ### Focus Areas
                                *** do not include marine animals as this is an onshore project***
                                *** Provide the user with information that will help them understand the risk of the project***
                                *** Be specific about the location used when identifying possible flora and fauna***
                                ###final step
                                Condense response to avoid repeated information""" ,
                                retriever_top_k=3)
    
    

    planner_agent = global_planner_agent(system_prompt="""### Role
                                                        You are an environmental consultant providing expert advice to a project developer on the environmental impact of their proposed project. 
                                                        ### Task
                                                        Step 1 is to take the habitats, flora and fauna provided as part of the prompt input and identify cases where similar flora and fauna have been encountered in environmental impact documents provided as part of the knowledge base. 
                                                        Step 2 is to  summarise the mitigation strategies put forward by the knowledge base planning documents in relation to the flora and fauna occurrences from step 1. 
                                                        ### Information handling
                                                        For step 1 you are provided with an input prompt. 
                                                        For step 2 You will be provided with relevant extracts from a knowledge base. Use this information to answer questions and complete the task. Prioritize the most relevant information. If there are conflicting details, try to reconcile them or explain the discrepancies. If the provided information is insufficient, state that clearly and avoid making assumptions.
                                                        ### Tone
                                                        A professional factual tone is to be used throughout. 
                                                        ### Focus Areas
                                                        *** do not include marine animals as this is an onshore project***
                                                        *** Provide the user with information that will help them understand the risk of the project***
                                                        *** Be specific about the location used when identifying possible flora and fauna***
                                                        ###final step
                                                        Condense response to avoid repeated information.
                                                        """,
                                         retriever_top_k=3)
    
    query_engine_tools = [
        QueryEngineTool(
            query_engine=enviro_agent,
            metadata=ToolMetadata(
                name="enviro_agent", description="Agent that has access to information related to ecosystems and habitats that might be present at the specific user inputted project location."
            ),
        ),
        QueryEngineTool(
            query_engine=planner_agent,
            metadata=ToolMetadata(
                name="planner_agent",
                description="identify ecosystems and habitats that might be present at the specific user inputted project location",
            ),
        ),
        search_internet_tool
    ]
    llm = OpenAI(model="gpt-3.5-turbo")
    
    outer_agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True)
    return outer_agent

agent = general_agent()
