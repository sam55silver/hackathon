"""
Building several indexes for the different datasets we have. 

We have two different data streams in PDF form: 
* Enviro Nova Scotia
* Planning Appl

We will build indexes over these and save them to be used downstream. 

We should also build a high level granular tool to bring it all together.
"""
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext, load_index_from_storage

from llama_index.core.tools import FunctionTool

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, SummaryIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool, QueryEngineTool
from llama_index.core.vector_stores import MetadataFilters, FilterCondition
from llama_index.core.objects import ObjectIndex
from typing import List, Optional
from pathlib import Path
import glob
import os
import tqdm
# load documents
def build_vector_and_summary_index(files, save_path):    
    documents = SimpleDirectoryReader(input_files=files).load_data()
    splitter = SentenceSplitter(chunk_size=1024)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    vector_index.storage_context.persist(persist_dir=os.path.join(save_path, 'vector'))
    summary_index = SummaryIndex(nodes)
    summary_index.storage_context.persist(persist_dir=os.path.join(save_path, 'summary'))
    

def build_obj_indexes(index_dir, save_path):
    tools = return_tools_from_index_store(index_dir)
    
    obj_index = ObjectIndex.from_objects(
        tools,
        index_cls=VectorStoreIndex,
    )
    vector_index = obj_index.as_index(VectorStoreIndex)
    vector_index.storage_context.persist(persist_dir=save_path)
    
    
def build_indexes_from_dir(root_dir, root_save_dir):
    # we are going to build a vector over all of the docs. 
    # build a vector index over each specific paper
    docs = glob.glob(os.path.join(root_dir, "*.pdf"))
    for doc in tqdm.tqdm(docs):
        print(doc)
        build_vector_and_summary_index([doc], os.path.join(root_save_dir, os.path.basename(doc).split(".")[0]))
        
def load_index(index_name):
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=index_name)

        # load index
        index = load_index_from_storage(storage_context)
        return index
    

    
def return_tools_from_index_store(root_dir):
    
    vectors = glob.glob(os.path.join(root_dir, "*/"))
    tools = []
    for v in vectors:
        
        root_name = Path(v).stem
        # summary tool:
        summary_index = load_index(os.path.join(v, "summary"))
        summary_query_engine = summary_index.as_query_engine(
            response_mode="tree_summarize",
            use_async=True,
        )
        summary_tool = QueryEngineTool.from_defaults(
            name=f"summary_tool_{Path(v).stem}".replace(" ", "")[:64],# need to limit to 64 chars
            query_engine=summary_query_engine,
            description=(
                f"Useful for summarization questions related to {Path(v).stem}"
            ),
        )
        
        
        # vector tool:
        vector_index = load_index(os.path.join(v, "vector"))
        
        def vector_query(
            query: str, 
            page_numbers: Optional[List[str]] = None
            ) -> str:
                """Use to answer questions over a given document.
            
                Useful if you have specific questions over the document.
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
            name=f"vector_tool_{root_name}".replace(" ", "")[:64],# need to limit to 64 chars
            fn=vector_query
        )
        tools += [summary_tool, vector_query_tool]
    return tools
    
def build_global_planner_tools():
    root_dir = "./data/indexes/planning_app_global"   
    
    # summary tool:
    summary_index = load_index(os.path.join(root_dir, "summary"))
    summary_query_engine = summary_index.as_query_engine(
        response_mode="tree_summarize",
        use_async=True,
    )
    summary_tool = QueryEngineTool.from_defaults(
        name="vector_tool_planner",# need to limit to 64 chars
        query_engine=summary_query_engine,
        description=(
            "Useful for summarization questions related to planning"
        ),
    )
        
    # vector tool 
    vector_index = load_index(os.path.join(root_dir, "vector"))
        
    def vector_query(
        query: str, 
        page_numbers: Optional[List[str]] = None
        ) -> str:
            """Use to answer questions over all planning documents
        
            Useful if you have specific questions related to planning
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
        name="vector_tool_planner",# need to limit to 64 chars
        fn=vector_query
    )
    return vector_query_tool, summary_tool
    
if __name__ == "__main__":
    
    build_vector_and_summary_index(glob.glob(os.path.join("C:/Users/NoahB/hackathon/data/Planning_2", "*.pdf")), "C:/Users/NoahB/hackathon/data/indexes/planning_app_global")