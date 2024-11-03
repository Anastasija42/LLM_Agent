"""
This module defines the `ToolInterface` class, which serves as an
abstract base class for all tools used within an agent system.

The `ToolInterface` class establishes a contract for the implementation
of various tools that can be utilized by the agent. Each tool must
provide a unique name and a description, as well as implement the
`use` method to define its specific functionality.

Usage:
    - Subclass the `ToolInterface` to create concrete tool implementations.
    - Implement the `use` method in the subclass to provide the tool's
      behavior.
    - Use instances of the subclasses in the agent to perform specific tasks
      based on user commands.
"""

from pydantic import BaseModel


class ToolInterface(BaseModel):
    """
    Abstract base class for a tool interface in an agent system.

    This class defines the structure that all tools within the agent
    must adhere to. Each tool should have a unique name and a
    description detailing its functionality. Subclasses must implement
    the `use` method to provide the specific behavior of the tool.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of the tool's purpose and usage.

    Methods:
        use(input_text: str) -> str:
            Executes the tool's functionality with the provided input
            and returns the result as a string. This method must be
            overridden in subclasses; otherwise, a NotImplementedError
            will be raised.
    """

    name: str
    description: str

    def use(self, input_text: str) -> str:
        """
        Executes the tool's functionality with the given input.

        This method is intended to be overridden by subclasses to
        implement specific tool behavior. It takes an input string
        and processes it according to the tool's functionality.

        Args:
            input_text (str): The input to be processed by the tool.

        Returns:
            str: The result of processing the input text.

        Raises:
            NotImplementedError: If this method is not implemented in a
            subclass.
        """
        raise NotImplementedError(
            "use() method not implemented"
        )  # Implement in subclass
