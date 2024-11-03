"""
This module provides a framework for a command-line Agent that interacts with the file system using
natural language prompts, leveraging tools and a language model for iterative task execution.

Classes:
    ChatLLM: An interface to a generative language model,
            configured to respond with structured content.
    Agent: The main agent class that processes user requests, selects tools to use, and iteratively
           completes tasks based on observations and responses from the language model.

Key Constants:
    FINAL_ANSWER_TOKEN: Token used to mark the final answer in the language model's response.
    OBSERVATION_TOKEN: Token used to denote observations after each tool action.
    THOUGHT_TOKEN: Token used to represent the agent's thought process in the prompt template.
    PROMPT_TEMPLATE: A structured template guiding the language model to interpret and act on
                    commands for managing files within a restricted directory.

Usage:
    Instantiate the Agent with an instance of ChatLLM and a list of tools.
    Use the `run` method to input a command, and the Agent will iteratively apply tools,
    navigating the file system and handling files based on the prompt.

Example:
    agent = Agent(
        llm=ChatLLM(),
        tools=[
            ListDirectoryTool(), ChangeDirectoryTool(), FileReaderTool(), CreateFileTool(),
            CreateDirectoryTool(), DeleteFileTool(), FileFinderTool(), FileReaderAnalyzerTool(),
            RenameFileTool(), AddContentTool(), DeleteContentTool()
        ]
    )
    result = agent.run("Do something.")
    print(result)

This setup limits all actions to a predefined directory (`example_dir`)
and ensures safe file handling.
"""

import re
import os
from typing import List, Dict, Tuple, Optional

import google.generativeai as genai  # type: ignore
from pydantic import BaseModel

import config
from llm_agent_api.base import ToolInterface


class ChatLLM(BaseModel):
    """
    A language model interface class for generating responses to natural language prompts using
    the Google Generative AI API.

    This class is configured with an API key and uses the "gemini-1.5-flash" model
    for generating content. The `generate` method allows the model to take in a prompt
    and optional stop sequences for structured output.
    It is designed to return a single response, optimized for short command-based
    interactions.

    Methods:
        generate(prompt: str, stop: List[str] = None) -> str:
            Generates a response based on the input prompt and optional stop sequences.
            Configures generation parameters, including `candidate_count`, `max_output_tokens`,
            and `temperature`, to control response style and length.

    Attributes:
        FINAL_ANSWER_TOKEN (str): Token used to identify the final answer in the generated content.
    """

    genai.configure(api_key=os.environ["API_KEY"])

    def generate(self, prompt: str, stop: Optional[List[str]] = None):
        """
        Generates a response from the language model based on the given prompt.

        Args:
            prompt (str): The input prompt for which the response is generated.
            stop (List[str], optional): A list of stop sequences that, if encountered, will end the
                generation of content. Defaults to None.

        Returns:
            str: The generated text response from the model.
        """
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                stop_sequences=stop,
                max_output_tokens=100,
                temperature=0,
            ),
        )
        return response.text


FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PROMPT_TEMPLATE = """You are an Agent for simple command line commands: navigate file system,
create/read/write/change/analyze files.
You are currently in this directory: {current_directory}.
Always keep in mind the current directory and if you need to change it to do the task.
Do the request given as best as you can using the following tools:

{tool_description}

You need to break down the request and iteratively execute the given tools.
Take into consideration your previous responses. Check what you have previously done, so you know what to do next.
If the observation is for example 'File not found', check if you gave the valid path or change the plan to add the file first.

If you need to delete the directory, call the Delete Directory tool from the upper directory. 

If you need to analyze all files, list them, and then use that observation for knowing what to analyze.
If you analyzed a file, remember that you did that, continue with the next! 
DO NOT LIST TWO TIMES IN A ROW!

Do not attempt to use the same tool with the same input twice in a row!

All the changes you do are inside the 'example_dir' directory, you are prohibited to exit this directory or access anything outside of it!

Use the following format:

Request: the input request you must do
Thought: comment on what you have done and what you will do next in the plan
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action

Observation: the result of the action, assess where you are in the overall plan of the request
... (this Thought/Action/Action Input/Observation repeats N times, use it until you finish the request)
Thought: I have now done the request!
Final Answer: your final statement that you've done the task requested

Begin!

Request: {question}
Thought: {previous_responses}
"""


class Agent(BaseModel):
    """
    An agent that processes a given request by iteratively selecting and using tools
    based on generated actions from a language model (LLM).

    The Agent uses a set of tools to fulfill command-line requests by following a structured
    prompt format, iteratively deciding on the best actions, and executing them while tracking
    previous actions. It stops when it reaches a final answer or completes the maximum loops.

    Attributes:
        llm (ChatLLM): The language model used to generate responses and action plans.
        tools (List[ToolInterface]): A list of available tools for performing actions.
        prompt_template (str): The template for structuring the agent's prompt.
        max_loops (int): The maximum number of iterations allowed
                                for the agent to fulfill a request.
        stop_pattern (List[str]): Stop sequences used to prevent unwanted
                                continuation in LLM responses.
    """

    llm: ChatLLM
    tools: List[ToolInterface]
    prompt_template: str = PROMPT_TEMPLATE
    max_loops: int = 20
    stop_pattern: List[str] = [f"\n{OBSERVATION_TOKEN}", f"\n\t{OBSERVATION_TOKEN}"]

    @property
    def tool_description(self) -> str:
        """
        Generates a description for each tool available to the agent.

        Returns:
            str: A newline-separated description list of each tool's name and purpose.
        """
        return "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        """
        Generates a comma-separated list of tool names.

        Returns:
            str: Comma-separated tool names as a single string.
        """
        return ",".join([tool.name for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, ToolInterface]:
        """
        Creates a dictionary of tools indexed by their names.

        Returns:
            Dict[str, ToolInterface]: A dictionary with tool names as keys and tools as values.
        """
        return {tool.name: tool for tool in self.tools}

    def run(self, question: str):
        """
        Executes the agent's main logic loop to fulfill the provided question.

        Uses the prompt template, tools, and the LLM to break down and execute the
        request step-by-step. Iterates up to `max_loops` times or stops if a final
        answer is reached.

        Args:
            question (str): The initial request or command to be processed.

        Returns:
            str: The final answer or result of executing the request.
        """
        previous_responses: List[str] = []

        previous_responses = []
        num_loops = 0
        prompt = self.prompt_template.format(
            current_directory=config.CURR_DIRECTORY,
            tool_description=self.tool_description,
            tool_names=self.tool_names,
            question=question,
            previous_responses="{previous_responses}",
        )

        while num_loops < self.max_loops:
            num_loops += 1
            curr_prompt = prompt.format(
                previous_responses="\n".join(previous_responses)
            )
            generated, tool, tool_input = self.decide_next_action(curr_prompt)
            if tool == "Final Answer":
                return tool_input
            if tool not in self.tool_by_names:
                raise ValueError(f"Unknown tool: {tool}")
            tool_result = self.tool_by_names[tool].use(tool_input)
            generated += f"\n{OBSERVATION_TOKEN} {tool_result}\n{THOUGHT_TOKEN}"
            print(generated)
            previous_responses.append(generated)

        return ""

    def decide_next_action(self, prompt: str) -> Tuple[str, str, str]:
        """
        Determines the next action to take based on the generated response from the LLM.

        Args:
            prompt (str): The formatted prompt for the LLM to generate a response.

        Returns:
            tuple[str, str, str]: The generated response, selected tool name, and tool input.
        """
        generated = self.llm.generate(prompt, stop=self.stop_pattern)
        tool, tool_input = self._parse(generated)
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        """
        Parses the generated response to extract the tool name and tool input.

        Identifies whether the response is the final answer or an intermediate action,
        and returns the relevant tool name and input.

        Args:
            generated (str): The LLM's generated output containing the action and input.

        Returns:
            Tuple[str, str]: A tuple with the tool name and tool input.

        Raises:
            ValueError: If the output format cannot be parsed for tool name or input.
        """
        if FINAL_ANSWER_TOKEN in generated:
            return "Final Answer", generated.split(FINAL_ANSWER_TOKEN)[-1].strip()

        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            raise ValueError(
                f"Output of LLM is not parsable for next tool use: `{generated}`"
            )

        tool = match.group(1).strip()
        tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')
