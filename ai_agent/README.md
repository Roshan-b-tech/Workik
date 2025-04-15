# AI Task Agent

An AI-powered agent that can execute tasks on your local computer. The agent uses AI to generate and execute plans for completing tasks, with user approval at each step.

## Features

- Task planning using AI
- Command and code execution
- Interactive approval workflow
- Error handling and task refinement
- Rich command-line interface
- Cross-platform support (Windows/Unix)

## Project Structure

```
ai_agent/
├── __init__.py          # Package initialization
├── cli.py              # Main command-line interface
├── ai_service.py       # AI API integration
├── test_netmind.py     # API testing utility
├── requirements.txt    # Project dependencies
└── .env               # Environment configuration
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your NetMind AI API key:
   - Create a `.env` file in the project root
   - Add your API key: `NETMIND_API_KEY=your_key_here`
   - Add the base URL: `NETMIND_BASE_URL=https://api.netmind.ai/inference-api/openai/v1`

## Usage

Run the agent from the command line:

```bash
python cli.py "your task here"
```

Example tasks:

- "Create a Python script that calculates fibonacci numbers"
- "Set up a new Python virtual environment and install requests package"
- "Create a simple web server using Flask"
- "Create a Java program to print even numbers"
- "Create an HTML boilerplate with modern styling"

## How it Works

1. **Task Input**

   - User provides a task description
   - Task is sent to AI for plan generation

2. **Plan Generation**

   - AI generates a step-by-step plan
   - Plan includes file creation and execution steps
   - Each step has type (command/code) and description

3. **User Approval**

   - Plan is displayed to user
   - User can approve or reject the plan
   - Rejected plans trigger a new attempt

4. **Execution**

   - Approved plans are executed step by step
   - Commands are run in the shell
   - Code is executed in Python environment

5. **Feedback Loop**
   - User confirms task success
   - Failed tasks trigger plan refinement
   - Process continues until success

## Architecture

### Core Components

1. **CLI Interface (`cli.py`)**

   - Handles user interaction
   - Manages task execution
   - Provides command-line interface

2. **AI Service (`ai_service.py`)**

   - Manages AI API communication
   - Generates and refines plans
   - Handles API authentication

3. **Package Initialization (`__init__.py`)**

   - Marks directory as Python package
   - Manages package-level imports
   - Handles package initialization

4. **Testing Utility (`test_netmind.py`)**
   - Verifies API connectivity
   - Tests plan generation
   - Validates API credentials

### Dependencies

- python-dotenv: Environment variable management
- requests: HTTP client for API communication
- pydantic: Data validation
- openai: OpenAI API client

## Development

To extend this project:

1. **Adding New Features**

   - Create new modules in the package
   - Update `__init__.py` for new imports
   - Add new command handlers in `cli.py`

2. **VSCode Extension**

   - Create a new VSCode extension project
   - Integrate the agent as a command provider
   - Add task input UI
   - Handle command execution

3. **Testing**
   - Run `test_netmind.py` to verify API setup
   - Test new features with sample tasks
   - Validate cross-platform compatibility

## Error Handling

The agent includes several error handling mechanisms:

1. **Plan Generation**

   - Retries with refined prompts
   - Validates JSON responses
   - Handles parsing errors

2. **Execution**

   - Captures command output
   - Handles execution errors
   - Provides error feedback

3. **User Interaction**
   - Validates user input
   - Handles approval workflow
   - Manages task refinement

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
