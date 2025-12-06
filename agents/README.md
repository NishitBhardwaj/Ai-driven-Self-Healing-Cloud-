# Agents Directory

This folder contains the code for all the AI agents in the **AI-driven multi-agent self-healing cloud infrastructure** project. Each agent performs a specific role in managing and automating cloud resources, detecting failures, scaling resources, handling user requests, and ensuring security.

## Agents Overview

- **Self-Healing Agent** (`/self-healing/`): Automatically detects and resolves cloud service failures. Monitors system health, identifies failures, and implements auto-recovery measures such as restarting services or scaling resources.

- **Scaling Agent** (`/scaling/`): Dynamically scales resources based on system load and usage. Adjusts cloud resources (containers, VMs) up or down based on demand to ensure optimal performance.

- **Task-Solving Agent** (`/task-solving/`): Handles user tasks such as uploading files, processing requests, and delegating tasks to other agents. Acts as a central coordinator for user-initiated operations.

- **Coding Agent** (`/coding/`): Generates and fixes code, automates debugging, and runs unit tests. Provides automated code generation based on user requirements and detects/fixes code errors.

- **Security Agent** (`/security/`): Monitors security breaches, detects threats, and ensures compliance. Continuously monitors for unauthorized access, vulnerabilities, and security threats.

- **Performance Monitoring Agent** (`/performance-monitoring/`): Tracks resource utilization and optimizes performance. Monitors key performance metrics and provides insights for system optimization.

- **Optimization Agent** (`/optimization/`): Ensures cost-efficient use of cloud resources. Manages resources for optimal performance while minimizing costs.

- **User Interaction Agent** (`/user-interaction/`): Handles user requests and provides real-time feedback. Interfaces with users through natural language processing and provides transparent explanations of agent actions.

## Agent Communication

Agents communicate with each other through:

- **Message Brokers**: RabbitMQ or Kafka for asynchronous communication
- **gRPC**: High-performance inter-agent communication
- **REST APIs**: For agent-to-agent HTTP-based interactions
- **Event-Driven Architecture**: Agents respond to system events and triggers

## How to Use

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/Ai-driven-Self-Healing-Cloud-.git
cd Ai-driven-Self-Healing-Cloud-/agents
```

### 2. Install Dependencies

For **Python agents**, install dependencies using `pip`:

```bash
pip install -r requirements.txt
```

For **Node.js agents**, install dependencies using `npm`:

```bash
npm install
```

### 3. Run an Agent

Example of running the **Self-Healing Agent**:

```bash
cd self-healing
python self_healing_agent.py
```

Example of running the **Task-Solving Agent**:

```bash
cd task-solving
python task_solving_agent.py
```

### 4. Test Agents

Run unit tests for individual agents:

```bash
# For Python agents
pytest self_healing_agent_tests.py

# For Node.js agents
npm test
```

Run integration tests to verify agent communication:

```bash
pytest tests/integration/test_agent_communication.py
```

## Agent Development Guidelines

1. **Modularity**: Each agent should be self-contained and independently deployable
2. **Communication**: Agents should use standardized communication protocols (gRPC, REST, Message Queues)
3. **Error Handling**: Implement robust error handling and logging
4. **Testing**: Write unit tests and integration tests for each agent
5. **Documentation**: Document agent APIs, configuration, and behavior

## Adding a New Agent

To add a new agent:

1. Create a new directory under `/agents/` with the agent name
2. Implement the agent following the existing agent structure
3. Add communication interfaces (gRPC, REST, or message queue handlers)
4. Write unit tests and integration tests
5. Update this README with the new agent's description
6. Add configuration files in `/config/agents-config/`

## Agent Configuration

Agent-specific configurations are stored in `/config/agents-config/`. Each agent should have its own configuration file that defines:

- Communication endpoints
- Thresholds and parameters
- Resource limits
- Behavior modes (auto/manual)

## Contributing

To contribute:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes following the coding standards
4. Write tests for your changes
5. Submit a pull request with a clear description

## Related Documentation

- Architecture documentation: `/docs/architecture/`
- API documentation: `/docs/api/`
- Configuration guide: `/config/README.md`
- Testing guide: `/tests/README.md`

