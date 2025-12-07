# n8n Workflow Agent

## Purpose

The n8n Workflow Agent is responsible for:
- Sending triggers to n8n workflows via webhook
- Receiving callback actions from n8n workflows
- Allowing n8n to control and orchestrate other agents
- Integrating external workflow automation with the agent system

## Responsibilities

1. **Webhook Integration**: Sends events to n8n webhooks
2. **Callback Processing**: Receives and processes n8n callbacks
3. **Workflow Orchestration**: Allows n8n to trigger agent actions
4. **Event Bridging**: Bridges between agent events and n8n workflows

## Endpoints

- `GET /health` - Health check endpoint
- `POST /trigger` - Trigger an n8n workflow
- `POST /webhook` - Receive callback from n8n
- `POST /action` - Execute an action
- `GET /status` - Get agent status

## Usage Example

When an error is detected:
1. Agent sends payload to n8n webhook
2. n8n workflow processes the event
3. n8n returns callback with action instructions
4. Agent executes the action

## Configuration

See `config.json` for n8n webhook URLs and workflow configurations.

## Events

- Publishes: `n8n.trigger`, `n8n.workflow.completed`
- Subscribes: `n8n.trigger`, `n8n.callback`

## n8n Workflow Examples

Three example workflows are provided in `/agents/n8n/workflows/`:

### 1. Error Auto-Heal Workflow
- **File**: `error-auto-heal.json`
- **Purpose**: Automatically heals errors detected in the system
- **Flow**: Webhook → LLM Analysis → Decision (Heal/Escalate) → Action → Callback
- **Usage**: Import into n8n and set webhook URL to `http://your-n8n-instance:5678/webhook/error-heal-trigger`

### 2. Code Debugging Pipeline
- **File**: `code-debugging-pipeline.json`
- **Purpose**: Automatically fixes code errors using LLM
- **Flow**: Webhook → LLM Fix → Save Patch → Return Code Diff
- **Usage**: Import into n8n and set webhook URL to `http://your-n8n-instance:5678/webhook/code-fix-trigger`

### 3. Security Intrusion Response
- **File**: `security-intrusion-response.json`
- **Purpose**: Responds to security alerts with automated actions
- **Flow**: Webhook → LLM Security Analysis → Firewall API → Callback
- **Usage**: Import into n8n and set webhook URL to `http://your-n8n-instance:5678/webhook/security-alert-trigger`

## Importing Workflows

1. Open n8n interface
2. Click "Import from File"
3. Select the JSON workflow file
4. Configure webhook URLs and API credentials
5. Activate the workflow

## Integration Code

The agent provides:
- `webhook.go` - Handles incoming n8n callbacks
- `trigger.go` - Sends events to n8n workflows
- `routes.go` - HTTP endpoints for webhook and trigger operations

