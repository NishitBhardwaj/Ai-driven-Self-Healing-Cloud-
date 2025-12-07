package core

import (
	"context"
	"encoding/json"
	"fmt"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// GRPCServer wraps gRPC server functionality for agents
type GRPCServer struct {
	server   *grpc.Server
	registry *AgentRegistry
	port     int
}

// NewGRPCServer creates a new gRPC server instance
func NewGRPCServer(port int) *GRPCServer {
	return &GRPCServer{
		server:   grpc.NewServer(),
		registry: GetRegistry(),
		port:     port,
	}
}

// Start starts the gRPC server
func (s *GRPCServer) Start() error {
	// Register service implementation will be done by individual agents
	// This is a base implementation
	return nil
}

// Stop stops the gRPC server
func (s *GRPCServer) Stop() {
	if s.server != nil {
		s.server.GracefulStop()
	}
}

// GetServer returns the underlying gRPC server
func (s *GRPCServer) GetServer() *grpc.Server {
	return s.server
}

// InvokeActionOnAgent invokes an action on an agent
func (s *GRPCServer) InvokeActionOnAgent(ctx context.Context, agentName, action string, params interface{}) (interface{}, error) {
	agent, err := s.registry.GetAgentByName(agentName)
	if err != nil {
		return nil, status.Errorf(codes.NotFound, "agent not found: %s", agentName)
	}

	// Convert params to JSON for transmission
	paramsJSON, err := json.Marshal(params)
	if err != nil {
		return nil, status.Errorf(codes.InvalidArgument, "invalid parameters: %v", err)
	}

	// Call agent's ReceiveEvent
	err = agent.ReceiveEvent(action, paramsJSON)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "action failed: %v", err)
	}

	return map[string]interface{}{
		"success": true,
		"agent":   agentName,
		"action":  action,
	}, nil
}

// Helper function to create error response
func createErrorResponse(err error) (interface{}, error) {
	return nil, status.Errorf(codes.Internal, "internal error: %v", err)
}

// Helper function to create success response with explanation
func createSuccessResponse(data interface{}, explanation string) interface{} {
	return map[string]interface{}{
		"success":     true,
		"data":        data,
		"explanation": explanation,
	}
}

