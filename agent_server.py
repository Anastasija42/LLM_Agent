from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import subprocess
from typing import Optional

app = FastAPI()

class CommandRequest(BaseModel):
    msg: str

class CommandResponse(BaseModel):
    msg: str

@app.post("/agent", response_model=CommandResponse)
async def execute_command(request: CommandRequest) -> CommandResponse:
    command = request.msg.strip().split()

    if command[0] == "ls":  # List directory contents
        output = "\n".join(os.listdir("."))  # List current directory
        return CommandResponse(msg=output)

    elif command[0] == "pwd":  # Print working directory
        return CommandResponse(msg=os.getcwd())

    elif command[0] == "cd":  # Change directory
        if len(command) < 2:
            raise HTTPException(status_code=400, detail="Directory not specified")
        try:
            os.chdir(command[1])
            return CommandResponse(msg=f"Changed directory to {os.getcwd()}")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Directory not found")

    elif command[0] == "touch":  # Create a new file
        if len(command) < 2:
            raise HTTPException(status_code=400, detail="File name not specified")
        open(command[1], 'a').close()  # Create the file
        return CommandResponse(msg=f"File '{command[1]}' created.")

    elif command[0] == "cat":  # Read a file
        if len(command) < 2:
            raise HTTPException(status_code=400, detail="File name not specified")
        try:
            with open(command[1], 'r') as file:
                content = file.read()
            return CommandResponse(msg=content)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")

    elif command[0] == "echo":  # Write to a file
        if len(command) < 3:
            raise HTTPException(status_code=400, detail="Insufficient arguments for echo")
        with open(command[1], 'w') as file:
            file.write(" ".join(command[2:]))  # Write to the file
        return CommandResponse(msg=f"Wrote to file '{command[1]}'.")

    else:
        raise HTTPException(status_code=400, detail="Unsupported command")

# Run the server with: uvicorn agent_server:app --host 0.0.0.0 --port 8000 --reload
