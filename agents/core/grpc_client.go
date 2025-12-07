package core

import (
	"context"
	"fmt"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

// GRPCClient provides gRPC client functionality for agent-to-agent communication
type GRPCClient struct {
	conn *grpc.ClientConn
}

// NewGRPCClient creates a new gRPC client
func NewGRPCClient(target string) (*GRPCClient, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	conn, err := grpc.DialContext(ctx, target, grpc.WithTransportCredentials(insecure.NewCredentials()), grpc.WithBlock())
	if err != nil {
		return nil, fmt.Errorf("failed to connect to %s: %w", target, err)
	}

	return &GRPCClient{conn: conn}, nil
}

// Close closes the gRPC client connection
func (c *GRPCClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

// GetConnection returns the underlying gRPC connection
func (c *GRPCClient) GetConnection() *grpc.ClientConn {
	return c.conn
}

// CallAgent calls an agent via gRPC
func (c *GRPCClient) CallAgent(ctx context.Context, agentName, action string, params interface{}) (interface{}, error) {
	// This will be implemented with actual proto service calls in Phase 5
	// For now, it's a placeholder
	return nil, fmt.Errorf("gRPC call not yet implemented - will be available in Phase 5")
}

