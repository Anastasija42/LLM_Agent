# LLM Command-Line Agent
This repository hosts a command-line Agent that interacts with the file system using natural language prompts, leveraging tools and a language model for iterative task execution. 

## Demo Video
Watch the demo video for a visual demonstration of the agent’s capabilities: 

https://github.com/user-attachments/assets/0a1e9749-5000-4e52-bbd7-6864860c113b


Key Components:
---------------
- **FastAPI**: A modern web framework for building APIs with Python 3.6+
                based on standard Python type hints.
- **Pydantic**: A data validation and settings management library used to
                validate incoming request payloads.
- **Langsmith Client**: A client to interact with the Langsmith API for
                managing and executing language model tasks.
- **Agent**: A class encapsulating the language model and command execution logic.
- **Command Tools**: A collection of tools that perform specific file system operations
            such as creating, deleting, renaming files and directories, and reading file content.

Features:
--------
- File Navigation and Operations: Supports commands to navigate directories, rename files, find files based on patterns, and search subfolders for specific files.
- Asynchronous Processing: Handles requests asynchronously for efficient command execution.
- Safe Access: Enforces secure file system operations within a specified directory (example_dir) to avoid unauthorized access.
- Configurable Tools: Utilizes a modular tool structure (e.g., ListDirectoryTool) for easy extension and maintenance.

Dependencies managed with Poetry:
--------------------------------
- Type checking with mypy
- Code quality enforcement with pylint
- Formatting with black
- FastAPI for the API layer

- **About the Language Model Integration**
This project uses Gemini 1.5 Flash, the language model from Google Generative AI, due to its robust performance and the fact that it’s freely accessible for experimentation.
While tools like LangChain offer various integrations with large language models, most of these integrations require paid services,
such as Vertex AI from Google or OpenAI, which necessitates account credits.
LangChain's built-in agent tools also don’t include free model integrations, which led to the decision to directly integrate Gemini 1.5 Flash instead.
This approach keeps the project accessible and free while leveraging powerful language processing capabilities.

Contact
-------
For questions, feedback, or collaboration inquiries, feel free to reach out!

- **Email**: [anastasijar01@gmail.com](mailto:anastasijar01@gmail.com)
- **LinkedIn**: [Anastasija Rakić](https://www.linkedin.com/in/anastasija-raki%C4%87-96725b256/)
- **GitHub**: [Anastasija42](https://github.com/Anastasija42)  
