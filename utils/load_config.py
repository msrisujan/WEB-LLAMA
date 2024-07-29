import os
from dotenv import load_dotenv
import yaml
from pyprojroot import here

class LoadConfig:

    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)
        self.gpt_model = app_config["gpt_model"]
        self.temperature = app_config["temperature"]
        self.llm_system_role = "You are a useful chatbot."
        self.llm_function_caller_system_role = app_config["llm_function_caller_system_role"]
        self.llm_system_role = app_config["llm_system_role"]

    

    