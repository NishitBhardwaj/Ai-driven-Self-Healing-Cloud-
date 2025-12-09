# Integration Tests for Multi-Agent Communication

This directory contains integration tests that verify agents can communicate effectively through message bus, gRPC, and REST APIs, and that agents take appropriate actions based on events.

## Test Files

### 1. Message Bus Tests (`message_bus_test.go`)

Tests agent communication through message bus:

- `TestMessageBusCommunication`: Tests message bus connection
- `TestErrorDetectedEvent`: Tests ERROR_DETECTED event reception
- `TestScalingRequiredEvent`: Tests SCALE_REQUIRED event reception
- `TestHealingRequiredEvent`: Tests HEALING_REQUIRED event reception
- `TestSecurityAlertEvent`: Tests SECURITY_ALERT event reception
- `TestTaskCreatedEvent`: Tests TASK_CREATED event reception
- `TestMultipleEventsSequential`: Tests multiple events in sequence
- `TestMessageBusPublishSubscribe`: Tests basic publish/subscribe functionality

**Run:**
```bash
go test -v ./tests/integration -run TestMessageBus
```

### 2. Event Routing Tests (`event_routing_test.go`)

Tests that Agent Router correctly routes events to proper agents:

- `TestEventRouterRoutesToCorrectAgent`: Tests routing to correct agents
- `TestEventRouterMultipleAgents`: Tests routing to multiple agents
- `TestEventRouterUnknownEvent`: Tests handling of unknown events
- `TestEventRouterConcurrentEvents`: Tests concurrent event routing
- `TestEventRouterEventOrdering`: Tests event ordering

**Run:**
```bash
go test -v ./tests/integration -run TestEventRouter
```

### 3. Agent Actions Tests (`agent_actions_test.go`)

Tests that agents take appropriate actions based on events:

- `TestAgentTakesActionOnErrorDetected`: Tests action on ERROR_DETECTED
- `TestAgentTakesActionOnScalingRequired`: Tests action on SCALE_REQUIRED
- `TestAgentTakesActionOnHealingRequired`: Tests action on HEALING_REQUIRED
- `TestAgentTakesActionOnSecurityAlert`: Tests action on SECURITY_ALERT
- `TestAgentActionChain`: Tests action chains (events trigger subsequent events)
- `TestAgentActionWithExplanation`: Tests that actions include explanations
- `TestAgentActionErrorHandling`: Tests error handling in actions
- `TestAgentActionConcurrency`: Tests concurrent agent actions
- `TestAgentActionResponseTime`: Tests agent action response time

**Run:**
```bash
go test -v ./tests/integration -run TestAgent
```

### 4. gRPC Communication Tests (`grpc_communication_test.go`)

Tests gRPC communication between agents:

- `TestGRPCConnection`: Tests gRPC connection establishment
- `TestGRPCCallAgent`: Tests gRPC call to agent
- `TestGRPCBiDirectionalStreaming`: Tests bi-directional streaming
- `TestGRPCErrorHandling`: Tests gRPC error handling
- `TestGRPCServiceDiscovery`: Tests gRPC service discovery

**Run:**
```bash
go test -v ./tests/integration -run TestGRPC
```

### 5. REST API Communication Tests (`rest_api_communication_test.go`)

Tests REST API communication between agents:

- `TestRESTAPIAgentCommunication`: Tests agent communication via REST
- `TestRESTAPIAgentAction`: Tests agent action via REST API
- `TestRESTAPIAgentStatus`: Tests agent status via REST API
- `TestRESTAPIAgentEvent`: Tests sending event to agent via REST
- `TestRESTAPIMultipleAgents`: Tests communication with multiple agents

**Run:**
```bash
go test -v ./tests/integration -run TestRESTAPI
```

## Running All Integration Tests

### Run all integration tests:
```bash
go test -v ./tests/integration/...
```

### Run with coverage:
```bash
go test -v ./tests/integration/... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Test Requirements

### Dependencies

Install required Go packages:
```bash
go get github.com/stretchr/testify/assert
go get github.com/stretchr/testify/require
go get google.golang.org/grpc
go get github.com/gorilla/mux
```

### Prerequisites

1. **Message Bus**: Tests require NATS or RabbitMQ (or will skip if unavailable)
2. **gRPC Server**: gRPC tests may require running gRPC server
3. **Agent Registry**: Tests use agent registry for agent management

## Test Coverage

### Message Bus Communication
- ✅ Connection establishment
- ✅ Event publishing
- ✅ Event subscription
- ✅ Multiple event types
- ✅ Sequential events
- ✅ Concurrent events

### Event Routing
- ✅ Routes to correct agents
- ✅ Routes to multiple agents
- ✅ Handles unknown events
- ✅ Concurrent routing
- ✅ Event ordering

### Agent Actions
- ✅ Actions on ERROR_DETECTED
- ✅ Actions on SCALE_REQUIRED
- ✅ Actions on HEALING_REQUIRED
- ✅ Actions on SECURITY_ALERT
- ✅ Action chains
- ✅ Explanations in actions
- ✅ Error handling
- ✅ Concurrency
- ✅ Response time

### gRPC Communication
- ✅ Connection establishment
- ✅ Agent calls
- ✅ Bi-directional streaming
- ✅ Error handling
- ✅ Service discovery

### REST API Communication
- ✅ Agent communication
- ✅ Agent actions
- ✅ Agent status
- ✅ Event sending
- ✅ Multiple agents

## Expected Test Results

All tests should pass:
- ✅ Message Bus: 8/8 tests passing
- ✅ Event Routing: 5/5 tests passing
- ✅ Agent Actions: 9/9 tests passing
- ✅ gRPC: 5/5 tests passing
- ✅ REST API: 5/5 tests passing

**Total: 32/32 tests passing**

## Troubleshooting

### Message Bus Connection Errors
- Ensure NATS/RabbitMQ is running
- Check message bus URL in configuration
- Tests will skip if message bus is unavailable

### gRPC Connection Errors
- Ensure gRPC server is running
- Check gRPC endpoint configuration
- Some tests may be placeholders for future implementation

### Agent Registration Errors
- Ensure agents are properly initialized
- Check agent registry is accessible
- Verify agent names match expected values

## Next Steps

After running tests:
1. Fix any failing tests
2. Add more comprehensive event scenarios
3. Test with actual message bus (NATS/RabbitMQ)
4. Test with actual gRPC server
5. Integrate with CI/CD pipeline

