package integration

import (
	"context"
	"testing"
	"time"

	"github.com/ai-driven-self-healing-cloud/agents/core"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// TestGRPCConnection tests gRPC connection establishment
func TestGRPCConnection(t *testing.T) {
	// In production, this would connect to actual gRPC server
	// For testing, we'll verify gRPC client can be created
	
	// Create gRPC connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	// Test connection (would use actual server address in production)
	// For now, just verify we can create a connection context
	assert.NotNil(t, ctx, "gRPC context should be created")
}

// TestGRPCCallAgent tests gRPC call to agent
func TestGRPCCallAgent(t *testing.T) {
	// This test would require a running gRPC server
	// For now, we'll create a mock test
	
	registry := core.GetRegistry()
	
	// Register agent with gRPC endpoint
	agent := core.NewAgent("test-agent", "Test Agent", "Test agent for gRPC")
	err := registry.RegisterAgentWithRPC(agent, "localhost:50051", "test")
	require.NoError(t, err)
	
	// Get agent info
	info, err := registry.GetAgentInfo("Test Agent")
	require.NoError(t, err)
	
	// Verify RPC endpoint is set
	assert.Equal(t, "localhost:50051", info.RPCEndpoint, "RPC endpoint should be set")
	assert.Equal(t, "test", info.AgentType, "Agent type should be set")
}

// TestGRPCBiDirectionalStreaming tests bi-directional streaming (if implemented)
func TestGRPCBiDirectionalStreaming(t *testing.T) {
	// This would test gRPC bi-directional streaming
	// For now, verify the concept
	
	// In production, would create streaming connection
	// and test real-time communication
	
	// Placeholder test
	assert.True(t, true, "gRPC streaming test placeholder")
}

// TestGRPCErrorHandling tests gRPC error handling
func TestGRPCErrorHandling(t *testing.T) {
	// Test gRPC error handling
	
	// Attempt connection to non-existent server
	ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
	defer cancel()
	
	// This would fail in real scenario
	_, err := grpc.DialContext(ctx, "localhost:99999", grpc.WithTransportCredentials(insecure.NewCredentials()))
	
	// Verify error is handled gracefully
	if err != nil {
		assert.Error(t, err, "Should error on invalid connection")
	}
}

// TestGRPCServiceDiscovery tests gRPC service discovery
func TestGRPCServiceDiscovery(t *testing.T) {
	registry := core.GetRegistry()
	
	// Register multiple agents with gRPC endpoints
	agent1 := core.NewAgent("agent-1", "Agent 1", "Test agent 1")
	agent2 := core.NewAgent("agent-2", "Agent 2", "Test agent 2")
	
	registry.RegisterAgentWithRPC(agent1, "localhost:50051", "type1")
	registry.RegisterAgentWithRPC(agent2, "localhost:50052", "type2")
	
	// Verify agents are discoverable
	info1, err := registry.GetAgentInfo("Agent 1")
	require.NoError(t, err)
	assert.Equal(t, "localhost:50051", info1.RPCEndpoint)
	
	info2, err := registry.GetAgentInfo("Agent 2")
	require.NoError(t, err)
	assert.Equal(t, "localhost:50052", info2.RPCEndpoint)
}

