"""
This module implements a FastAPI server that serves as an API for executing commands
using a language model agent. The agent integrates various tools for file and directory
operations, allowing users to interact with the file system through natural language commands.

Key Components:
---------------
- **FastAPI**: A modern web framework for building APIs with Python 3.6+
                based on standard Python type hints.
- **Pydantic**: A data validation and settings management library used to
                validate incoming request payloads.
- **Langsmith Client**: A client to interact with the Langsmith API for
                managing and executing language model tasks.
- **Agent**: A class that encapsulates the language model and command execution logic.
- **Command Tools**: A collection of tools that perform specific file system operations
            such as creating, deleting, renaming files and directories, and reading file content.

API Endpoints:
--------------
- **POST /agent**: Accepts a command in JSON format
                    and returns the result of executing the command using the agent.
    - Request Body:
        - `msg`: The command to execute.
    - Response:
        - Returns a JSON object with the execution result or an error message.

- **GET /**: A root endpoint that returns a welcome message.
- **GET /favicon.ico**: Returns an empty response for favicon requests (optional).

Usage:
------
To run the server, execute the following command in the terminal:
    uvicorn agent_server:app --host localhost --port 8000 --reload

Example Request:
----------------
To post a request to the agent endpoint, you can use curl as follows:
    curl -X POST "localhost:8000/agent" -H "Content-Type: application/json"
    -d '{"msg": "Can you make a new file in dir1 with a joke in it?"}'

This will trigger the agent to process the command and return the result.
"""

import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from langsmith import Client
from agent import Agent, ChatLLM
from llm_agent_api.command_tools import (
    ListDirectoryTool,
    ChangeDirectoryTool,
    CreateFileTool,
    CreateDirectoryTool,
    DeleteFileTool,
    DeleteDirectoryTool,
    FileFinderTool,
    FileReaderAnalyzerTool,
    FileReaderTool,
    RenameFileTool,
    AddContentTool,
    DeleteContentTool,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Client()

app = FastAPI()


class CommandRequest(BaseModel):
    """
    Represents a request to the command execution API.

    Attributes:
        msg (str): The command message that the user wants to execute.
    """

    msg: str


class CommandResponse(BaseModel):
    """
    Represents the response returned by the command execution API.

    Attributes:
        msg (str): The result or output of executing the command.
    """

    msg: str


agent = Agent(
    llm=ChatLLM(),
    tools=[
        ListDirectoryTool(),
        ChangeDirectoryTool(),
        CreateFileTool(),
        CreateDirectoryTool(),
        DeleteFileTool(),
        DeleteDirectoryTool(),
        FileFinderTool(),
        FileReaderAnalyzerTool(),
        FileReaderTool(),
        RenameFileTool(),
        AddContentTool(),
        DeleteContentTool(),
    ],
)


@app.post("/agent", response_model=CommandResponse)
async def execute_command(request: CommandRequest) -> CommandResponse:
    """
    Executes a command received from the client and returns the result.

    This endpoint processes the command contained in the request, utilizes the
    agent to run the command, and returns the output as a CommandResponse object.

    Args:
        request (CommandRequest): The request containing the command to be executed.

    Returns:
        CommandResponse: A CommandResponse object containing the result of the executed command,
        or an error message if the command cannot be processed.
    """
    command = request.msg.strip()

    try:
        result = agent.run(command)
        response = CommandResponse(msg=result)
        return response

    except (ValueError, TypeError, RuntimeError) as e:

        logger.error("Known error occurred: %s", str(e))

        return CommandResponse(
            msg="Couldn't process the request, rephrase it and try again!"
        )


# Root route
@app.get("/")
async def read_root():
    """
    Root endpoint for the API.

    This endpoint serves as a health check and provides a welcome message
    indicating that the LLM Command Execution API is operational.

    Returns:
        dict: A JSON response containing a welcome message.
    """
    return {"msg": "Welcome to the LLM Command Execution API!"}


# Favicon route (Optional, you can return an empty response)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Handles requests for the favicon icon.

    This endpoint returns an empty JSON response with a status code of 204
    (No Content) to indicate that there is no favicon available for the API.

    Returns:
        JSONResponse: An empty JSON response with a status code of 204.
    """
    return JSONResponse(content={}, status_code=204)
