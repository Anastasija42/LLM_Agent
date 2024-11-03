"""
This module provides a collection of command tools that can be used
within the agent system to perform various file and directory
operations. Each tool is implemented as a subclass of the
`ToolInterface`, allowing for a consistent interface and behavior
across different tools.

Tools included in this module may encompass functionalities such as:
- Listing directories
- Changing directories
- Creating and deleting files and directories
- Renaming files
- Reading and analyzing file content

Each tool is designed to encapsulate specific behaviors related to file
system manipulation, providing an easy-to-use interface for the agent
to interact with the file system based on user commands.

Usage:
    - Import the necessary tools from this module.
    - Instantiate the desired tool classes and utilize their `use`
      method to execute commands.
    - Integrate these tools into the agent's workflow to enhance its
      capabilities.

"""

import os
import fnmatch
import config
from llm_agent_api.base import ToolInterface


class ListDirectoryTool(ToolInterface):
    """
    A tool for listing the contents of a specified directory.

    This tool allows users to retrieve a list of files and directories within
    a specified path. If no input is provided, it defaults to the 'example_dir'
    directory. The output includes the names and sizes of files, as well as
    indicators for directories.
    """

    name: str = "List Directory"
    description: str = (
        "Lists files in the specified directory."
        " Input should be a valid directory inside the 'example_dir' directory "
        " or ' ' for the default 'example_dir' directory."
    )

    def use(self, input_text: str) -> str:
        """
        Lists the contents of the specified directory.

        This method checks if the input text corresponds to a valid directory.
        If the input is empty, it defaults to the current directory specified
        by `config.CURR_DIRECTORY`. It returns a formatted string listing
        all files and directories within the specified path.

        Args:
            input_text (str): The relative path of the directory to list.
                              If empty, the current directory is used.

        Returns:
            str: A formatted string that lists all files and directories in
                 the specified directory or an error message if the directory
                 is invalid or if an error occurs during the listing process.
        """
        directory = os.path.join(config.CURR_DIRECTORY, input_text.strip())

        # Use default directory if input is empty
        if not input_text.strip():
            directory = config.CURR_DIRECTORY

        if not os.path.isdir(directory):
            return "Invalid directory."

        try:
            items = os.listdir(directory)
            formatted_output = f"Directory listing for: {directory}\n"
            formatted_output += "-----------------------------------\n"
            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    formatted_output += f"[DIR]  {item}\n"
                else:
                    file_size = os.path.getsize(item_path)
                    formatted_output += f"[FILE] {item}  ({file_size} bytes)\n"
            return formatted_output.strip()

        except FileNotFoundError:
            return f"Error: The directory '{directory}' does not exist."
        except PermissionError:
            return f"Error: Permission denied when accessing '{directory}'."
        except OSError as e:
            return f"Error listing directory: {str(e)}"


class ChangeDirectoryTool(ToolInterface):
    """
    Tool for changing the current working directory.

    This tool allows the user to change the current working directory to a specified
    valid directory inside the 'example_dir' directory. It navigates to the new
    directory if necessary.
    """

    name: str = "Change Directory"
    description: str = (
        "Changes the current working directory. Navigates to one if needed."
        "Input should be a valid directory name inside the 'example_dir' directory."
    )

    def use(self, input_text: str) -> str:
        """
        Changes the current working directory to the specified input directory.

        Args:
            input_text (str): The name of the directory to change to, relative to
                              the 'example_dir'.

        Returns:
            str: A message indicating the result of the operation:
                 - Success message if the directory is changed successfully.
                 - "Forbidden directory." if attempting to navigate to the parent directory.
                 - "Invalid directory." if the specified directory does not exist.
        """
        new_dir = os.path.join("example_dir", input_text.strip())

        if os.path.isdir(new_dir):
            if new_dir == "example_dir/..":
                return "Forbidden directory."
            config.CURR_DIRECTORY = new_dir
            return f"Changed directory to {new_dir}"
        return "Invalid directory."


class CreateFileTool(ToolInterface):
    """
    Tool for creating a new file in the current directory.

    This tool allows the user to create a new file within the current working
    directory. The file is created with the specified name, and if the file
    already exists, it will be overwritten.
    """

    name: str = "Create File"
    description: str = (
        "Creates a new file in the current directory." "Input should be the file name."
    )

    def use(self, input_text: str) -> str:
        """
        Creates a new file with the specified name in the current directory.

        Args:
            input_text (str): The name of the file to be created. This should be a
                              valid file name.

        Returns:
            str: A message indicating the result of the operation:
                 - Success message if the file is created.
                 - An error message if the file cannot be created, detailing the
                   issue encountered.
        """
        file_path = os.path.join(config.CURR_DIRECTORY, input_text.strip())

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")  # Create an empty file
            return f"File '{input_text}' created."
        except (IOError, OSError) as e:  # Catch specific file operation exceptions
            return f"Error creating file: {str(e)}"


class CreateDirectoryTool(ToolInterface):
    """
    Tool for creating a new directory in the current directory.

    This tool allows the user to create a new directory within the current working
    directory. If the directory already exists, it will notify the user accordingly.
    """

    name: str = "Create Directory"
    description: str = (
        "Creates a new directory in the current directory. "
        "Input should be the directory name."
    )

    def use(self, input_text: str) -> str:
        """
        Creates a new directory with the specified name in the current directory.

        Args:
            input_text (str): The name of the directory to be created. This should be a
                              valid directory name.

        Returns:
            str: A message indicating the result of the operation:
                 - Success message if the directory is created.
                 - Message indicating the directory already exists if applicable.
                 - An error message if the directory cannot be created, detailing the
                   issue encountered.
        """
        new_dir = os.path.join(config.CURR_DIRECTORY, input_text.strip())

        try:
            os.makedirs(new_dir)
            return f"Directory '{input_text}' created."
        except FileExistsError:
            return "Directory already exists."
        except PermissionError:
            return f"Permission denied: Unable to create directory '{input_text}'."
        except OSError as e:
            return f"Error creating directory: {str(e)}"


class DeleteFileTool(ToolInterface):
    """
    Tool for deleting a file in the current directory.

    This tool allows the user to delete a specified file from the current working
    directory. If the file does not exist, an appropriate message will be returned.
    """

    name: str = "Delete File"
    description: str = (
        "Deletes a file in the current directory. " "Input should be the file name."
    )

    def use(self, input_text: str) -> str:
        """
        Deletes the specified file from the current directory.

        Args:
            input_text (str): The name of the file to be deleted. This should be a
                              valid file name.

        Returns:
            str: A message indicating the result of the operation:
                 - Success message if the file is deleted.
                 - Message indicating that the file was not found if applicable.
                 - An error message if the file cannot be deleted, detailing the
                   issue encountered.
        """
        path = input_text.strip()
        path = os.path.normpath(path)
        base_dir = os.path.normpath("example_dir")
        if path.startswith(base_dir):
            # Remove the base directory prefix and any leading separator
            path = path[len(base_dir) :].lstrip(os.sep)

        file_path = os.path.join(config.CURR_DIRECTORY, path)

        try:
            os.remove(file_path)
            return f"File '{input_text}' deleted."
        except FileNotFoundError:
            return "File not found."
        except PermissionError:
            return f"Permission denied: Unable to delete file '{input_text}'."
        except OSError as e:
            return f"Error deleting file: {str(e)}"


class DeleteDirectoryTool(ToolInterface):
    """
    Tool for deleting a directory in the current directory.

    This tool allows the user to delete a specified directory from the current working
    directory. The directory must be empty to be deleted. If the directory does not exist
    or is not empty, an appropriate message will be returned.
    """

    name: str = "Delete Directory"
    description: str = (
        "Deletes a directory in the current directory. "
        "Input should be the directory name."
    )

    def use(self, input_text: str) -> str:
        """
        Deletes the specified directory from the current directory.

        Args:
            input_text (str): The name of the directory to be deleted. This should be a
                              valid directory name.

        Returns:
            str: A message indicating the result of the operation:
                 - Success message if the directory is deleted.
                 - Message indicating that the directory was not found if applicable.
                 - Message indicating that the directory is not empty if that is the
                   issue.
                 - An error message if the directory cannot be deleted, detailing the
                   issue encountered.
        """
        dir_path = os.path.join(config.CURR_DIRECTORY, input_text.strip())

        try:
            os.rmdir(dir_path)
            return f"Directory '{input_text}' deleted."
        except FileNotFoundError:
            return "Directory not found."
        except PermissionError:
            return f"Permission denied: Unable to delete directory '{input_text}'."
        except OSError:
            return "Directory not empty or not found."


class FileFinderTool(ToolInterface):
    """
    Tool for finding files in the current directory and its subdirectories.

    This tool allows the user to search for files that match a specified filename pattern
    within the current working directory and all its subdirectories. The search is performed
    using a pattern like '*.txt' to locate matching files.
    """

    name: str = "Find Files"
    description: str = (
        "Finds files in the current directory and subdirectories that match a specified pattern. "
        "Input should be a filename pattern (e.g., '*.txt') to locate matching files."
    )

    def use(self, input_text: str) -> str:
        """
        Searches for files matching the specified pattern in the current directory
        and its subdirectories.

        Args:
            input_text (str): The filename pattern to match (e.g., '*.txt').
                            Leading and trailing whitespace will be ignored.

        Returns:
            str: A message indicating the result of the search:
                 - A comma-separated list of matching file paths if found.
                 - A message indicating that no files were found if applicable.
        """
        current_dir = config.CURR_DIRECTORY
        matching_files = []
        pattern = input_text.strip()
        for root, _, files in os.walk(current_dir):
            for filename in fnmatch.filter(files, pattern):
                matching_files.append(os.path.join(root, filename))

        if not matching_files:
            return "No files found matching the pattern."

        return ", ".join(matching_files)


class FileReaderAnalyzerTool(ToolInterface):
    """
    Tool for reading and analyzing a file's content for specified keywords.

    This tool allows the user to read the content of a specified file and analyze it for
    the presence of specified keywords. The input should include the file path followed by
    a comma-separated list of keywords to search within the file.
    """

    name: str = "Read and Analyze File"
    description: str = (
        "Reads the content of a specified file and analyzes it for specified keywords. "
        "Input should be the file path, followed by a comma-separated list of keywords."
    )

    def use(self, input_text: str) -> str:
        """
        Reads the content of the specified file and analyzes it for the provided keywords.

        Args:
            input_text (str): The input text containing the file path and keywords,
                              separated by a comma. The first part is the file path,
                              and the second part (optional) is a comma-separated
                              list of keywords.

        Returns:
            str: A message indicating the result of the analysis:
                 - A report on the number of times each keyword is found in the file's content.
                 - An error message if the file is not found or if reading the file fails.
        """
        # Split input to get the file path and keywords
        parts = input_text.strip().split(",", 1)
        if len(parts) < 1:
            return "Please provide a file path and keywords."

        file_path = parts[0].strip()
        file_path = os.path.join(config.CURR_DIRECTORY, file_path)
        keywords = [k.strip() for k in parts[1].split(",")] if len(parts) > 1 else []

        if not os.path.isfile(file_path):
            return f"File not found: {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return self.analyze_content(content, keywords)
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except IsADirectoryError:
            return f"The path provided is a directory, not a file: {file_path}"
        except UnicodeDecodeError:
            return "Error reading file: Unable to decode the file content."

    def analyze_content(self, content: str, keywords: list) -> str:
        """
        Analyzes the content of the file for specified keywords.

        Args:
            content (str): The content of the file to analyze.
            keywords (list): A list of keywords to search for in the content.

        Returns:
            str: A summary of the analysis, indicating how many times each keyword
                 was found in the content, or if a keyword was not found.
        """
        results = []
        for keyword in keywords:
            count = content.lower().count(keyword.lower())
            if count > 0:
                results.append(f"Keyword '{keyword}' found {count} times.")
            else:
                results.append(f"Keyword '{keyword}' not found.")

        return "\n".join(results)


class FileReaderTool(ToolInterface):
    """
    Tool for reading the content of a specified file.

    This tool allows the user to read the content of a file. The input should be
    a valid file path. If the file is found, its content is returned; otherwise,
    an error message is provided.
    """

    name: str = "Read File"
    description: str = (
        "Reads the content of a specified file. Input should be the file path."
    )

    def use(self, input_text: str) -> str:
        """
        Reads the content of the specified file.

        Args:
            input_text (str): The input text containing the file path to read.

        Returns:
            str: The content of the file if found, or an error message indicating
                 that the file was not found or an issue occurred while reading it.
        """
        path = input_text.strip()
        path = os.path.normpath(path)
        base_dir = os.path.normpath("example_dir")
        if path.startswith(base_dir):
            # Remove the base directory prefix and any leading separator
            path = path[len(base_dir):].lstrip(os.sep)

        file_path = os.path.join(config.CURR_DIRECTORY, path)

        if not os.path.isfile(file_path):
            return f"File not found: {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return content
        except OSError as e:
            return f"Error reading file: {str(e)}"


class RenameFileTool(ToolInterface):
    """
    Tool for renaming files in the current directory.

    This tool allows the user to rename files by specifying the current filename
    and the new name. The input should include both names separated by a space.
    If the file exists, it is renamed; otherwise, an error message is returned.
    """

    name: str = "Rename File"
    description: str = (
        "Renames files in the current directory based on a pattern. "
        "Input should specify the current filename and the new name."
    )

    def use(self, input_text: str) -> str:
        """
        Renames a file in the current directory.

        Args:
            input_text (str): The input text containing the current filename
                              and the new name, separated by a space.

        Returns:
            str: A message indicating the result of the rename operation,
                 including success or specific error messages.
        """
        old_name, new_name = input_text.split(",")
        old_name = old_name.strip()
        new_name = new_name.strip()
        old_path = os.path.join(config.CURR_DIRECTORY, old_name)
        new_path = os.path.join(config.CURR_DIRECTORY, new_name)

        try:
            os.rename(old_path, new_path)
            return f"Renamed '{old_name}' to '{new_name}'."
        except FileNotFoundError:
            return "File not found."
        except OSError as e:
            return f"Error renaming file: {str(e)}"


class AddContentTool(ToolInterface):
    """
    Tool for appending content to a specified file.

    This tool allows users to append specified content to an existing file
    in the current directory. The input should include the file name and the
    content to be added, separated by a comma. If the file does not exist,
    an error message is returned.
    """

    name: str = "Add Content"
    description: str = (
        "Appends specified content to a file in the current directory. "
        "Input should be the file name followed by the content to add, separated by a ','."
    )

    def use(self, input_text: str) -> str:
        """
        Appends content to a specified file.

        Args:
            input_text (str): The input text containing the file name and
                              content to add, separated by a comma.

        Returns:
            str: A message indicating the result of the append operation,
                 including success or specific error messages.
        """
        parts = input_text.split(",", 1)
        if len(parts) != 2:
            return "Invalid input format. Provide a file name followed by content."

        file_name, content_to_add = parts
        file_path = os.path.join(config.CURR_DIRECTORY, file_name.strip())

        if not os.path.isfile(file_path):
            return "File not found."

        try:
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(f"\n{content_to_add.strip()}")
            return f"Content added to '{file_name}'."
        except OSError as e:
            return f"Error adding content: {str(e)}"


class DeleteContentTool(ToolInterface):
    """
    Tool for deleting lines containing specified text from a file.

    This tool allows users to delete lines from a specified file in the
    current directory that contain a given text. The input should include
    the file name and the text to delete, separated by a comma. If the file
    does not exist, an error message is returned.
    """

    name: str = "Delete Content"
    description: str = (
        "Deletes lines containing specified text from a file in the current directory. "
        "Input should be the file name followed by the text to delete."
    )

    def use(self, input_text: str) -> str:
        """
        Deletes lines containing specified text from a file.

        Args:
            input_text (str): The input text containing the file name and
                              text to delete, separated by a comma.

        Returns:
            str: A message indicating the result of the delete operation,
                 including success or specific error messages.
        """
        parts = input_text.split(",", 1)
        if len(parts) != 2:
            return "Invalid input format. Provide a file name followed by the text to delete."

        file_name, text_to_delete = parts
        file_path = os.path.join(config.CURR_DIRECTORY, file_name.strip())

        if not os.path.isfile(file_path):
            return "File not found."

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            with open(file_path, "w", encoding="utf-8") as file:
                for line in lines:
                    if text_to_delete not in line:
                        file.write(line)

            return f"Deleted lines containing '{text_to_delete}' from '{file_name}'."
        except OSError as e:
            return f"Error deleting content: {str(e)}"
