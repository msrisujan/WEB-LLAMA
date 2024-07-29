from typing import Dict
import inspect
import json
from inspect import Parameter
from pydantic import create_model
from utils.web_search import WebSearch
from typing import List, Dict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()

os.environ["GROQ_API_KEY"]= os.getenv("GROQ_API_KEY")

class Apputils:

    @staticmethod
    def jsonschema(f) -> Dict:
        kw = {n: (o.annotation, ... if o.default == Parameter.empty else o.default)
              for n, o in inspect.signature(f).parameters.items()}
        s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    
        return dict(name=f.__name__, description=f.__doc__, parameters=s)
    
    @staticmethod
    def wrap_functions() -> List:
        return [
            Apputils.jsonschema(WebSearch.retrieve_web_search_results),
            Apputils.jsonschema(WebSearch.web_search_text),
            Apputils.jsonschema(WebSearch.web_search_pdf),
            Apputils.jsonschema(WebSearch.get_instant_web_answer),
            Apputils.jsonschema(WebSearch.web_search_image),
            Apputils.jsonschema(WebSearch.web_search_video),
            Apputils.jsonschema(WebSearch.web_search_news),
            Apputils.jsonschema(WebSearch.web_search_map),
        ]
    
    @staticmethod
    def execute_json_function(response) -> List:
        func_name: str = response.tool_calls[0]['name']
        func_args: Dict = response.tool_calls[0]['args']
        print(func_args)
        # Call the function with the given arguments
        if func_name == 'retrieve_web_search_results':
            result = WebSearch.retrieve_web_search_results.invoke(input=func_args)
        elif func_name == 'web_search_text':
            result = WebSearch.web_search_text.invoke(input=func_args)
        elif func_name == 'web_search_pdf':
            result = WebSearch.web_search_pdf.invoke(input=func_args)
        elif func_name == 'web_search_image':
            result = WebSearch.web_search_image.invoke(input=func_args)
        elif func_name == 'web_search_video':
            search_query = func_args.get('keywords')
            result = WebSearch.web_search_video.invoke(input=func_args)
        elif func_name == 'web_search_news':
            result = WebSearch.web_search_news.invoke(input=func_args)
        elif func_name == 'get_instant_web_answer':
            result = WebSearch.get_instant_web_answer.invoke(input=func_args)
        elif func_name == 'web_search_map':
            result = WebSearch.web_search_map.invoke(input=func_args)
        else:
            raise ValueError(f"Function '{func_name}' not found.")

        return result
    
    @staticmethod
    def ask_llm_function_caller(gpt_model: str, temperature: float, messages: List, function_json_list: List):
        llm = ChatGroq(model="llama3-70b-8192", temperature=temperature)
        llama3_with_tools = llm.bind_tools(function_json_list)
        try:
            ai_msg = llama3_with_tools.invoke(messages)
        except:
            ai_msg = llm.invoke(messages)

        return ai_msg
    
    @staticmethod
    def ask_llm_chatbot(gpt_model: str, temperature: float, messages: List):
        llm = ChatGroq(model="llama3-70b-8192", temperature=temperature)
        response = llm.invoke(messages)
        return response