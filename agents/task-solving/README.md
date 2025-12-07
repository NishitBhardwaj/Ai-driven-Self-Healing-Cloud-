# Task-Solving Agent

## Purpose

The Task-Solving Agent is responsible for:
- Parsing and interpreting user tasks
- Converting tasks into actionable agent commands
- Using LLM to understand task intent and context
- Coordinating with other agents to complete tasks

## Responsibilities

1. **Task Parsing**: Receives user tasks in natural language
2. **Intent Interpretation**: Uses LLM to understand what the user wants
3. **Action Generation**: Breaks down tasks into specific agent actions
4. **Task Coordination**: Publishes events to trigger other agents

## Endpoints

- `GET /health` - Health check endpoint
- `POST /task` - Submit a new task for processing
- `POST /action` - Execute an action
- `GET /status` - Get agent status

## Configuration

See `config.json` for agent-specific configuration including:
- LLM provider and model settings
- Task processing limits
- Message bus topics

## Usage

The agent automatically starts when registered in the system. Tasks can be submitted via HTTP POST to `/task` endpoint.

## Events

- Publishes: `task.created`, `task.completed`
- Subscribes: `task.created`, `task.completed`

