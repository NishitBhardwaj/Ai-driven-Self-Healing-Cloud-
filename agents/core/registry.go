package core

import (
	"fmt"
	"sync"
)

// AgentInfo stores agent metadata including RPC endpoint
type AgentInfo struct {
	Agent      BaseAgent
	RPCEndpoint string
	AgentType   string
}

// AgentRegistry stores and manages all registered agents
type AgentRegistry struct {
	agents map[string]*AgentInfo
	mu     sync.RWMutex
}

var globalRegistry *AgentRegistry
var registryOnce sync.Once

// GetRegistry returns the global agent registry instance (singleton)
func GetRegistry() *AgentRegistry {
	registryOnce.Do(func() {
		globalRegistry = &AgentRegistry{
			agents: make(map[string]*AgentInfo),
		}
	})
	return globalRegistry
}

// RegisterAgent registers an agent in the registry
func (r *AgentRegistry) RegisterAgent(agent BaseAgent) error {
	return r.RegisterAgentWithRPC(agent, "", "")
}

// RegisterAgentWithRPC registers an agent with RPC endpoint information
func (r *AgentRegistry) RegisterAgentWithRPC(agent BaseAgent, rpcEndpoint, agentType string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if agent == nil {
		return fmt.Errorf("cannot register nil agent")
	}

	name := agent.GetName()
	if name == "" {
		return fmt.Errorf("agent must have a non-empty name")
	}

	// Check if agent with same name already exists
	if _, exists := r.agents[name]; exists {
		return fmt.Errorf("agent with name '%s' already registered", name)
	}

	r.agents[name] = &AgentInfo{
		Agent:       agent,
		RPCEndpoint: rpcEndpoint,
		AgentType:   agentType,
	}
	return nil
}

// GetAgentByName retrieves an agent by its name
func (r *AgentRegistry) GetAgentByName(name string) (BaseAgent, error) {
	info, err := r.GetAgentInfo(name)
	if err != nil {
		return nil, err
	}
	return info.Agent, nil
}

// GetAgentInfo retrieves agent info including RPC endpoint
func (r *AgentRegistry) GetAgentInfo(name string) (*AgentInfo, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	info, exists := r.agents[name]
	if !exists {
		return nil, fmt.Errorf("agent '%s' not found in registry", name)
	}

	return info, nil
}

// ListAgents returns a list of all registered agent names
func (r *AgentRegistry) ListAgents() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	names := make([]string, 0, len(r.agents))
	for name := range r.agents {
		names = append(names, name)
	}

	return names
}

// GetAgentCount returns the number of registered agents
func (r *AgentRegistry) GetAgentCount() int {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return len(r.agents)
}

// GetAllAgents returns all registered agents
func (r *AgentRegistry) GetAllAgents() map[string]BaseAgent {
	r.mu.RLock()
	defer r.mu.RUnlock()

	// Return a copy to prevent external modification
	agents := make(map[string]BaseAgent)
	for name, info := range r.agents {
		agents[name] = info.Agent
	}
	return agents
}

// InvokeAction invokes an action on an agent by name
func (r *AgentRegistry) InvokeAction(agentName, action string, params interface{}) error {
	agent, err := r.GetAgentByName(agentName)
	if err != nil {
		return err
	}

	// Try to call the action via ReceiveEvent
	// In Phase 5, this will be enhanced with proper action routing
	return agent.ReceiveEvent(action, params)
}

