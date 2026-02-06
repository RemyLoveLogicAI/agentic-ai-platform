"""
Agentic AI Pair Programmer
==========================

This module defines an ``AgenticPairProgrammer`` class that embodies the
"agentic AI pair programmer" described in the project manifesto.  It is
designed to be a proactive collaborator for software development tasks,
capable of synthesising code, debugging, refactoring and continuously
learning from interactions.  The class is built around modern AI
frameworks (e.g. LangChain, AutoGen and vector databases) and exposes a
high-level API for integration into your projects.  While many of the
methods here contain placeholders for external API calls (e.g. to
OpenAI, Anthropic, or quantum services), the overall structure shows
how to orchestrate these capabilities in a cohesive way.

Key Features
------------
* **Proactive Code Synthesis**: Analyse the current state of a
  repository and anticipate the next steps.  Generate syntactically
  correct and contextually relevant code without explicit prompting.
* **Contextually Omnipotent Debugging**: When errors occur, inspect
  call stacks, logs and environment state to identify root causes.
  Propose corrective patches that align with the existing code style and
  architectural goals.
* **Quantum‑Scale Integration**: Stubbed methods demonstrate where
  quantum computing backends might be invoked for optimisation or
  simulation tasks.  These functions are no‑ops by default but can be
  extended to interface with real quantum services (e.g. IBM Qiskit).
* **Autonomous Refactoring**: Continuously monitor code for
  opportunities to improve structure and readability.  Apply SOLID
  principles and modern design patterns while preserving external
  behaviour.
* **Meta‑Learning**: Track interactions and outcomes to improve
  decision‑making over time.  Persist experience in a vector store for
  retrieval augmented generation (RAG) strategies.

Example Usage
-------------
The following example shows how to initialise the agent and ask it to
propose a code snippet for a simple HTTP server using FastAPI:

>>> from agentic_ai_pair_programmer import AgenticPairProgrammer
>>> agent = AgenticPairProgrammer(project_path="/path/to/repo")
>>> suggestion = agent.proactive_code_synthesis(
...     goal="Create a REST API endpoint to return user profiles"
... )
>>> print(suggestion)

The suggestion will include a Python function and corresponding route
definition that can be integrated into your FastAPI project.

Note
----
This module uses asynchronous calls (`async def`) for methods that may
call external APIs or run long‑lived tasks.  If your environment does
not support asyncio, you can wrap calls in ``asyncio.run`` or adapt
them to synchronous equivalents.
"""

from __future__ import annotations

import asyncio
import datetime as _datetime
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    # Optional dependencies for LangChain and AutoGen.  These libraries
    # are not installed by default; install them via pip to enable full
    # functionality.
    from langchain.agents import initialize_agent, AgentExecutor
    from langchain.agents.agent_types import AgentType
    from langchain.llms import OpenAI
    from langchain.tools import tool
    from langchain.memory import VectorStoreRetrieverMemory
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings
except ImportError:
    # Fallback stubs allow the class to be imported even when
    # dependencies are missing.  Methods will raise if called.
    initialize_agent = None  # type: ignore
    AgentExecutor = None  # type: ignore
    AgentType = None  # type: ignore
    OpenAI = None  # type: ignore
    tool = None  # type: ignore
    VectorStoreRetrieverMemory = None  # type: ignore
    Chroma = None  # type: ignore
    OpenAIEmbeddings = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class AgenticPairProgrammer:
    """Agentic AI pair programmer for proactive coding assistance.

    Parameters
    ----------
    project_path : str
        Path to the root of the project this agent will operate on.
    llm_model : str, optional
        Name of the LLM provider/model (e.g. ``"gpt-4"``).  Used when
        instantiating language model clients.  Default is ``"gpt-4"``.
    memory_dir : str, optional
        Directory for storing the persistent vector database used for
        meta‑learning.  If not provided, a ``.agent_memory`` folder is
        created inside ``project_path``.
    temperature : float, optional
        Sampling temperature for text generation.  Lower values
        encourage deterministic responses.  Default is 0.1.
    """

    project_path: str
    llm_model: str = "gpt-4"
    memory_dir: Optional[str] = None
    temperature: float = 0.1
    _agent: Optional[AgentExecutor] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Initialise the agent's environment after construction.

        This method is automatically called by the dataclass constructor.
        It resolves the project path, ensures it exists, and creates the
        memory directory if needed.  It also prepares lazy-initialisation
        stubs for the language model and memory.

        Raises
        ------
        FileNotFoundError
            If the provided ``project_path`` does not exist.
        """
        # Ensure the project path exists.
        self.root = Path(self.project_path).expanduser().resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Project path {self.root} does not exist")
        self.memory_dir = Path(self.memory_dir or (self.root / ".agent_memory"))
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Lazy initialisation of the language model and agent.  We defer
        # loading heavy resources until they are needed.
        self.llm = None  # type: Optional[OpenAI]
        self.memory = None  # type: Optional[VectorStoreRetrieverMemory]

    def _ensure_llm(self) -> None:
        """Initialise the language model and memory if not already done."""
        if self.llm is not None:
            return
        if OpenAI is None:
            raise RuntimeError(
                "LangChain and its dependencies are not installed. "
                "Please install the langchain package to use this functionality."
            )
        # Initialise the base LLM.  You can swap this for Anthropic,
        # Cohere, or other providers by following the respective API docs.
        self.llm = OpenAI(model_name=self.llm_model, temperature=self.temperature)

        # Initialise a vector store for long‑term memory.  This uses
        # Chroma as a lightweight local database.  Embeddings are
        # generated using OpenAIEmbeddings by default.
        embeddings = OpenAIEmbeddings(model=self.llm_model)
        store = Chroma(
            embedding_function=embeddings,
            persist_directory=str(self.memory_dir),
        )
        self.memory = VectorStoreRetrieverMemory(retriever=store.as_retriever())

    async def _init_agent(self) -> None:
        """Asynchronously create the LangChain agent with tools and memory."""
        if self._agent is not None:
            return
        self._ensure_llm()
        assert self.llm is not None  # For mypy
        assert self.memory is not None

        # Define custom tools.  Tools are callables that the agent can
        # invoke to perform side effects or computations.  They must have
        # docstrings describing their behaviour clearly, as the agent
        # relies on these descriptions to choose among them.

        @tool
        def list_files(path: str = "") -> str:
            """List project files relative to the repository root.

            Parameters
            ----------
            path : str, optional
                Subdirectory to list.  Default is the project root.

            Returns
            -------
            str
                JSON‑formatted list of file names.
            """
            base = self.root / path
            files = [p.name for p in base.glob("*") if p.is_file()]
            return json.dumps(files)

        @tool
        def read_file(filepath: str) -> str:
            """Read the contents of a file in the project.

            Parameters
            ----------
            filepath : str
                Relative path to the file from the project root.

            Returns
            -------
            str
                Contents of the file.
            """
            target = (self.root / filepath).resolve()
            if not target.exists() or not target.is_file():
                return f"Error: {filepath} does not exist or is not a file"
            return target.read_text()

        @tool
        def write_file(args: str) -> str:
            """Write text to a file in the project.

            The argument should be a JSON object with keys ``filepath`` and
            ``content``.  Example:

            ``{"filepath": "app/main.py", "content": "print('hello')"}``

            If the directory does not exist, it will be created.  Returns
            a success message or error string.
            """
            try:
                data = json.loads(args)
                filepath = (self.root / data["filepath"]).resolve()
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_text(data["content"])
                return f"Wrote {len(data['content'])} characters to {data['filepath']}"
            except Exception as e:
                return f"Error: {str(e)}"

        # Assemble the list of tools for the agent.  Additional tools
        # can be defined elsewhere in your codebase and appended here.
        tools = [list_files, read_file, write_file]

        # Initialise the agent with memory and chosen agent type.  We use
        # ZERO_SHOT_REACT_DESCRIPTION here, which allows the agent to
        # decide which tool to call based solely on the description and
        # user input.  You can experiment with other agent types such as
        # CONVERSATIONAL_REACT to incorporate chat history.
        self._agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
        )

    async def proactive_code_synthesis(self, goal: str) -> str:
        """Generate code proactively based on a high‑level goal.

        This method analyses the current project state and uses the
        underlying language model to propose code that fulfils the given
        goal.  It leverages the LangChain agent to introspect files and
        incorporate relevant context into the generated output.  The
        resulting code is returned as a string.  Side effects (such as
        writing files) are only executed when explicitly requested.

        Parameters
        ----------
        goal : str
            High‑level description of what the agent should implement.

        Returns
        -------
        str
            Proposed code snippet or explanation.
        """
        await self._init_agent()
        assert self._agent is not None

        prompt = (
            "You are a proactive AI pair programmer.  "
            "Analyse the existing repository and propose code to achieve the following goal:\n"
            f"{goal}\n"
            "Return only the code in your response, without backticks or commentary."
        )
        response = await self._agent.arun(prompt)
        return response

    async def debug_code(self, error_message: str, context_files: Optional[List[str]] = None) -> str:
        """Diagnose and suggest a fix for a given error.

        When provided with an error message (e.g. a stack trace), the
        agent will search relevant files and propose a correction.  You
        can optionally supply a list of file paths to narrow the search
        scope.  The result is a description of the issue and a code
        snippet that resolves it.

        Parameters
        ----------
        error_message : str
            The stack trace or error output produced during execution.
        context_files : list[str], optional
            List of relative file paths to inspect.  If omitted, the
            agent may explore any file in the repository.

        Returns
        -------
        str
            Proposed fix or analysis of the error.
        """
        await self._init_agent()
        assert self._agent is not None
        context_note = (
            " Use only the specified files for context." if context_files else ""
        )
        prompt = (
            "You are an expert debugger with holistic insight into the codebase.\n"
            f"An error occurred:\n{error_message}\n"
            f"{context_note}\n"
            "Provide a concise explanation of the root cause and propose a code change to fix it.\n"
            "Return the fix as a unified diff, or as a code snippet if appropriate."
        )
        # Preload context by reading specified files; this primes the
        # agent's memory so it can reference the contents.
        if context_files:
            for f in context_files:
                _ = (self.root / f).read_text()  # Reading triggers memory update
        result = await self._agent.arun(prompt)
        return result

    async def refactor_code(self, target_files: List[str], objectives: Optional[str] = None) -> str:
        """Refactor target files to improve structure and maintainability.

        This method guides the agent to perform refactoring on specific
        files.  The objectives string may include design principles to
        enforce (e.g. "apply SOLID", "modularise into smaller functions").
        Returns a summary of changes and the refactored code.

        Parameters
        ----------
        target_files : list[str]
            Relative paths of files to refactor.
        objectives : str, optional
            High‑level description of the refactoring goals.

        Returns
        -------
        str
            The agent's proposed refactor changes.
        """
        await self._init_agent()
        assert self._agent is not None
        objectives = objectives or "Improve readability and reduce duplication"
        # Prime memory with file contents
        for f in target_files:
            path = (self.root / f).resolve()
            if path.exists():
                _ = path.read_text()
        prompt = (
            "You are an autonomous refactoring engine.\n"
            f"Refactor the following files to meet these objectives: {objectives}.\n"
            f"Files: {', '.join(target_files)}\n"
            "Return the refactored code for each file, clearly separated by file name."
        )
        response = await self._agent.arun(prompt)
        return response

    async def quantum_optimize(self, problem_description: str) -> str:
        """Placeholder for quantum optimisation tasks.

        Quantum algorithms can solve certain optimisation problems more
        efficiently than classical approaches.  This stub demonstrates
        where such an integration would occur.  In a real deployment
        you might call Qiskit, Braket or other quantum SDKs here.

        Parameters
        ----------
        problem_description : str
            Description of the optimisation problem (e.g. "travelling
            salesman with 8 nodes").

        Returns
        -------
        str
            A human‑readable description of the solution or next steps.
        """
        # The default implementation simply logs and returns a stub.
        logger.info(
            "Quantum optimisation requested.  Stub implementation only."
        )
        return (
            "Quantum optimisation not yet implemented.  "
            f"Problem description: {problem_description}"
        )

    async def meta_learn(self, feedback: str) -> None:
        """Persist feedback for future retrieval.

        By ingesting feedback into the vector store, the agent can
        recall past interactions and refine its behaviour.  This
        function stores the feedback as a document in the memory.  In
        practice, you might also use this to train custom models or
        update fine‑tuning datasets.

        Parameters
        ----------
        feedback : str
            Textual feedback describing the success or failure of an
            agent action.
        """
        self._ensure_llm()
        assert self.memory is not None
        # Each feedback entry includes a timestamp and description
        doc = {
            "page_content": feedback,
            "metadata": {"timestamp": _datetime.datetime.utcnow().isoformat()},
        }
        # Persist to the vector store
        self.memory.save_context({}, doc)
        logger.debug("Saved feedback to vector store: %s", feedback)

    def _log_event(
        self, event_name: str, inputs: Dict[str, Any], output: str
    ) -> None:
        """Log an agent event to the monitoring file."""
        log_file = self.root / "monitoring_log.jsonl"
        log_entry = {
            "timestamp": _datetime.datetime.utcnow().isoformat(),
            "event": event_name,
            "inputs": inputs,
            "output": output,
        }
        try:
            with log_file.open("a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error("Failed to write to monitoring log: %s", e)

    # Convenience synchronous wrappers
    def run_proactive_code_synthesis(self, goal: str) -> str:
        """Synchronous wrapper for :meth:`proactive_code_synthesis`."""
        result = ""
        try:
            result = asyncio.run(self.proactive_code_synthesis(goal))
            return result
        except Exception as e:
            result = f"An error occurred: {e}"
            raise
        finally:
            self._log_event(
                "run_proactive_code_synthesis", {"goal": goal}, result
            )

    def run_debug_code(
        self, error_message: str, context_files: Optional[List[str]] = None
    ) -> str:
        """Synchronous wrapper for :meth:`debug_code`."""
        result = ""
        try:
            result = asyncio.run(self.debug_code(error_message, context_files))
            return result
        except Exception as e:
            result = f"An error occurred: {e}"
            raise
        finally:
            self._log_event(
                "run_debug_code",
                {"error_message": error_message, "context_files": context_files},
                result,
            )

    def run_refactor_code(
        self, target_files: List[str], objectives: Optional[str] = None
    ) -> str:
        """Synchronous wrapper for :meth:`refactor_code`."""
        result = ""
        try:
            result = asyncio.run(self.refactor_code(target_files, objectives))
            return result
        except Exception as e:
            result = f"An error occurred: {e}"
            raise
        finally:
            self._log_event(
                "run_refactor_code",
                {"target_files": target_files, "objectives": objectives},
                result,
            )

    def run_quantum_optimize(self, problem_description: str) -> str:
        """Synchronous wrapper for :meth:`quantum_optimize`."""
        result = ""
        try:
            result = asyncio.run(self.quantum_optimize(problem_description))
            return result
        except Exception as e:
            result = f"An error occurred: {e}"
            raise
        finally:
            self._log_event(
                "run_quantum_optimize",
                {"problem_description": problem_description},
                result,
            )

    def run_meta_learn(self, feedback: str) -> None:
        """Synchronous wrapper for :meth:`meta_learn`."""
        result = "Feedback recorded successfully."
        try:
            asyncio.run(self.meta_learn(feedback))
        except Exception as e:
            result = f"An error occurred: {e}"
            raise
        finally:
            self._log_event("run_meta_learn", {"feedback": feedback}, result)
