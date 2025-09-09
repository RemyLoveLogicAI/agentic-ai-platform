"""
Web Application for the Agentic AI Pair Programmer
=================================================

This Flask application provides a simple web interface for interacting with the
AgenticPairProgrammer. It allows users to submit goals, view results, and
monitor the agent's activity through a dashboard.

Routes:
  - /: The main page with a form to submit a goal to the agent.
  - /submit: Handles the form submission and displays the agent's output.
  - /dashboard: Displays a log of all agent interactions.
"""

from flask import Flask, render_template, request
from agentic_ai_pair_programmer import AgenticPairProgrammer
import os
import json

# --- IMPORTANT ---
# The agent requires an OpenAI API key to function.
# This application will not start unless the OPENAI_API_KEY environment
# variable is set.
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError(
        "The OPENAI_API_KEY environment variable is not set. "
        "Please set it before running the application."
    )

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the main page with the goal submission form."""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    Handles the goal submission from the main page.
    Initializes the agent, runs the code synthesis, and displays the result.
    """
    goal = request.form.get('goal')
    result = None
    try:
        if not goal:
            raise ValueError("Please provide a goal.")

        # Initialize the agent. The project path is the current directory.
        agent = AgenticPairProgrammer(project_path=".")

        # This synchronous method will call the agent and log the event.
        result = agent.run_proactive_code_synthesis(goal)

    except Exception as e:
        # The agent's run method logs the full error. We display a
        # user-friendly message on the UI.
        result = f"An error occurred: {e}"

    # Re-render the main page with the result and the original goal.
    return render_template('index.html', result=result, goal=goal)

@app.route('/dashboard')
def dashboard():
    """
    Renders the monitoring dashboard page.
    Reads the monitoring log file and displays its contents.
    """
    logs = []
    log_file = "monitoring_log.jsonl"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            for line in f:
                try:
                    # Each line in the file is a separate JSON object.
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip any corrupted or empty lines in the log file.
                    continue
    # Reverse the logs to show the most recent entries first.
    logs.reverse()
    return render_template('dashboard.html', logs=logs)

if __name__ == '__main__':
    # Runs the Flask application. Host '0.0.0.0' makes it accessible from
    # outside the container.
    app.run(host='0.0.0.0', port=8080)
