"""
Environment Configuration Script.

This script sets up the necessary environment variables required for the
integration with LangChain and LangSmith APIs. It prompts the user to enter
their LangSmith API key securely.

Environment Variables:
    LANGCHAIN_TRACING_V2 (str): A flag to enable tracing for LangChain version 2.
    LANGSMITH_ENDPOINT (str): The endpoint URL for the LangSmith API.
    LANGCHAIN_API_KEY (str): The API key for accessing the LangChain service,
                             which is input securely by the user.
    LANGCHAIN_PROJECT (str): The name of the project being utilized within
                             LangChain (set to "llm_agent_api").

Usage:
    Run this script to configure the environment variables before executing
    the application that relies on LangChain and LangSmith functionalities.
"""

import getpass
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
os.environ["LANGCHAIN_PROJECT"] = "llm_agent_api"
