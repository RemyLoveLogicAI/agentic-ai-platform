# Agentic AI Pair Programmer

This repository contains the `AgenticPairProgrammer`, a Python class that embodies an "agentic AI pair programmer". It is designed to be a proactive collaborator for software development tasks, capable of synthesising code, debugging, refactoring, and continuously learning from interactions.

The class is built around modern AI frameworks like LangChain and vector databases, and it exposes a high-level API for integration into your projects.

## Key Features

*   **Proactive Code Synthesis**: Analyse the current state of a repository and anticipate the next steps. Generate syntactically correct and contextually relevant code without explicit prompting.
*   **Contextually Omnipotent Debugging**: When errors occur, inspect call stacks, logs, and environment state to identify root causes. Propose corrective patches that align with the existing code style and architectural goals.
*   **Quantum-Scale Integration**: Stubbed methods demonstrate where quantum computing backends might be invoked for optimisation or simulation tasks.
*   **Autonomous Refactoring**: Continuously monitor code for opportunities to improve structure and readability. Apply SOLID principles and modern design patterns while preserving external behaviour.
*   **Meta-Learning**: Track interactions and outcomes to improve decision-making over time. Persist experience in a vector store for retrieval-augmented generation (RAG) strategies.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/example/agentic-ai-pair-programmer.git
    cd agentic-ai-pair-programmer
    ```

2.  **Install dependencies:**

    The project dependencies are listed in the `requirements.txt` file. Install them using pip:

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment:**

    The agent uses the OpenAI API for its language model capabilities. You need to have an OpenAI API key. It is recommended to set this key as an environment variable:

    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```

## Web UI Usage

This project includes a simple web interface to interact with the agent and a dashboard to monitor its activity.

1.  **Run the web server:**
    ```bash
    python app.py
    ```

2.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8080`.

    -   The **Home** page provides a form to submit goals to the agent.
    -   The **Dashboard** page displays a log of all agent activities.

**Note:** Ensure you have set the `OPENAI_API_KEY` environment variable as described in the "Setup" section before running the application.

## Command-Line Usage

The following example shows how to initialise the agent and ask it to propose a code snippet for a simple HTTP server using FastAPI.

```python
from agentic_ai_pair_programmer import AgenticPairProgrammer

# Initialize the agent, pointing it to your project's repository
agent = AgenticPairProgrammer(project_path="/path/to/your/repo")

# Ask the agent to generate code for a specific goal
suggestion = agent.run_proactive_code_synthesis(
    goal="Create a REST API endpoint to return user profiles"
)

print(suggestion)
```

The `suggestion` will include a Python function and a corresponding route definition that can be integrated into a FastAPI project.

### Asynchronous API

This module uses asynchronous calls (`async def`) for methods that may call external APIs or run long-lived tasks. If your environment supports `asyncio`, you can `await` these methods directly. For synchronous contexts, convenient wrapper methods (e.g., `run_proactive_code_synthesis`) are provided, which run the async methods using `asyncio.run()`.
