# XAI Integration Guide - Final Explainability Layer

## Overview

This guide explains how to integrate the Final Explainability Layer (XAI) into every agent's decision-making process. The XAI layer ensures that every action taken by an agent is fully explained with Chain-of-Thought (CoT) reasoning.

---

## Components

### 1. Explainable Interface (`xai.go`)

Every agent must implement the `Explainable` interface:

```go
type Explainable interface {
    ExplainAction(input interface{}, output interface{}) string
    ExplainActionDetailed(input interface{}, output interface{}) *DecisionExplanation
    GetReasoningChain() []ReasoningStep
    GetConfidence() float64
    GetAlternativeActions() []string
}
```

### 2. XAI Engine (`xai.go`)

The `XAIEngine` provides explainability services:

```go
xaiEngine := core.NewXAIEngine(logger, llmReasoning)
explanation, err := xaiEngine.GenerateExplanation(
    agentID,
    agentName,
    actionTaken,
    input,
    output,
    mode,
    confidence,
    problem,
    context,
)
```

### 3. LLM Reasoning Integration (`xai_llm_integration.go`)

Integrates with Python LLM reasoning service for Chain-of-Thought reasoning.

### 4. Reasoning Logger (`xai_logger.go`)

Logs explanations to ELK Stack or file system.

---

## Integration Steps

### Step 1: Initialize XAI Engine in Agent

```go
package selfhealing

import (
    "github.com/ai-driven-self-healing-cloud/agents/core"
)

type SelfHealingAgent struct {
    xaiEngine *core.XAIEngine
    // ... other fields
}

func NewSelfHealingAgent() *SelfHealingAgent {
    // Initialize logger
    logger := core.GetDefaultLogger()
    
    // Initialize LLM reasoning
    llmReasoning := core.NewLLMReasoningIntegration()
    
    // Initialize XAI engine
    xaiEngine := core.NewXAIEngine(logger, llmReasoning)
    
    return &SelfHealingAgent{
        xaiEngine: xaiEngine,
        // ... other initializations
    }
}
```

### Step 2: Generate Explanation After Action

```go
func (a *SelfHealingAgent) Heal(request *HealingRequest) (*HealingResult, error) {
    // ... perform healing action
    
    // Generate explanation
    explanation, err := a.xaiEngine.GenerateExplanation(
        a.GetID(),
        a.GetName(),
        action,
        request,
        result,
        core.AutoMode, // or ManualMode
        0.95, // confidence level
        request.Error,
        map[string]interface{}{
            "pod_name": request.ServiceID,
            "failure_type": request.FailureType,
        },
    )
    
    if err != nil {
        // Handle error
    }
    
    // Log explanation (automatically done by XAI engine)
    // Explanation is logged to ELK Stack or file
    
    return result, nil
}
```

### Step 3: Implement Explainable Interface

```go
func (a *SelfHealingAgent) ExplainAction(input interface{}, output interface{}) string {
    if a.xaiEngine == nil {
        return "Action performed by Self-Healing Agent"
    }
    
    explanation, err := a.xaiEngine.GenerateExplanation(
        a.GetID(),
        a.GetName(),
        "heal",
        input,
        output,
        core.AutoMode,
        0.95,
        "Service failure detected",
        nil,
    )
    
    if err != nil {
        return "Unable to generate explanation"
    }
    
    return explanation.Reasoning
}

func (a *SelfHealingAgent) ExplainActionDetailed(input interface{}, output interface{}) *core.DecisionExplanation {
    // Similar implementation but returns DecisionExplanation
}

func (a *SelfHealingAgent) GetReasoningChain() []core.ReasoningStep {
    // Return reasoning chain from last explanation
}

func (a *SelfHealingAgent) GetConfidence() float64 {
    return 0.95 // Return agent's confidence level
}

func (a *SelfHealingAgent) GetAlternativeActions() []string {
    return []string{"restart_pod", "rebuild_deployment", "rollback"}
}
```

---

## Chain-of-Thought Reasoning Example

### Scaling Agent CoT Reasoning

The Scaling Agent follows this 5-step process:

**Step 1: CPU Usage Detection**
```
Input: CPU usage = 95%, threshold = 85%
Output: Alert triggered, severity = high
Reasoning: CPU usage exceeds 85% threshold by 10%
```

**Step 2: Historical Data Analysis**
```
Input: Last 30 minutes of data
Output: Trend = increasing, average = 88%, peak = 95%
Reasoning: CPU has been consistently high for 10 minutes
```

**Step 3: Transformer Forecasting**
```
Input: Current metrics, forecast horizon = 5 minutes
Output: Predicted CPU = 98%, predicted latency = 300ms
Reasoning: Model predicts continued increase, high risk
```

**Step 4: User Confirmation (Manual Mode)**
```
Input: Options = [scale_up, optimize], recommendation = scale_up
Output: User selected = scale_up, approved = true
Reasoning: User reviewed analysis and approved scaling
```

**Step 5: Action Execution**
```
Input: Action = scale_up, current = 3, target = 5
Output: Status = success, replicas = 5
Reasoning: Successfully scaled to 5 replicas
```

**Step 6: Agent Report**
```
Input: Action = scale_up
Output: Report generated, explanation sent
Reasoning: Comprehensive report with full CoT reasoning
```

---

## Confidence Levels

### Auto Mode
- **Default Confidence**: 95% (0.95)
- Used when agent acts automatically
- High confidence required for auto-execution

### Manual Mode
- **Default Confidence**: 85% (0.85)
- Used when user approval is required
- Lower confidence indicates need for human review

### Setting Confidence

```go
confidence := 0.95 // Auto mode
if mode == core.ManualMode {
    confidence = 0.85
}

// Or calculate based on factors
confidence := calculateConfidence(risk, impact, historicalSuccess)
```

---

## Logging Explanations

### ELK Stack Integration

Set environment variable:
```bash
export ELASTICSEARCH_URL=http://localhost:9200
```

The logger will automatically send explanations to Elasticsearch.

### File Logging (Fallback)

If ELK Stack is not available, explanations are logged to:
```
logs/xai/xai_YYYY-MM-DD.log
logs/xai/reasoning_YYYY-MM-DD.log
```

### Log Format

```json
{
  "@timestamp": "2024-01-01T12:00:00Z",
  "agent_id": "scaling-001",
  "agent_name": "Scaling Agent",
  "action_taken": "scale_up",
  "reasoning": "...",
  "reasoning_chain": [...],
  "confidence_level": 0.85,
  "mode": "manual",
  "alternative_actions": ["optimize", "restart_service"],
  "context": {...},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Dashboard Integration

### Displaying Explanations

The explanations can be displayed in the dashboard using the JSON format:

```javascript
// Fetch explanation from API
const explanation = await fetch('/api/v1/explanations/decision-id');

// Display in UI
displayExplanation(explanation);
```

### Real-Time Updates

Use WebSocket or Server-Sent Events to receive real-time explanation updates:

```javascript
const ws = new WebSocket('ws://api/explanations/stream');
ws.onmessage = (event) => {
    const explanation = JSON.parse(event.data);
    updateDashboard(explanation);
};
```

---

## Example: Complete Agent Integration

```go
package scaling

import (
    "github.com/ai-driven-self-healing-cloud/agents/core"
)

type ScalingAgent struct {
    *core.Agent
    xaiEngine *core.XAIEngine
}

func NewScalingAgent() *ScalingAgent {
    logger := core.GetDefaultLogger()
    llmReasoning := core.NewLLMReasoningIntegration()
    xaiEngine := core.NewXAIEngine(logger, llmReasoning)
    
    return &ScalingAgent{
        Agent: core.NewAgent("scaling-001", "Scaling Agent", "Dynamically scales resources"),
        xaiEngine: xaiEngine,
    }
}

func (a *ScalingAgent) Scale(request *ScalingRequest) (*ScalingResult, error) {
    // Detect CPU overload
    if request.CPUUsage > 85.0 {
        // Step 1: Problem detection
        problem := fmt.Sprintf("CPU usage is at %.1f%%", request.CPUUsage)
        
        // Step 2: Analyze historical data
        historicalData := a.analyzeHistoricalData()
        
        // Step 3: Predict future demand
        forecast := a.predictFutureDemand()
        
        // Step 4: User confirmation (if manual mode)
        mode := a.getMode()
        if mode == core.ManualMode {
            // Present options to user
            options := a.generateOptions()
            // Wait for user selection
        }
        
        // Step 5: Execute scaling
        result := a.executeScaling(action)
        
        // Generate explanation with CoT reasoning
        explanation, err := a.xaiEngine.GenerateExplanation(
            a.GetID(),
            a.GetName(),
            "scale_up",
            request,
            result,
            mode,
            0.85, // Manual mode confidence
            problem,
            map[string]interface{}{
                "cpu_usage": request.CPUUsage,
                "historical": historicalData,
                "forecast": forecast,
            },
        )
        
        if err != nil {
            return nil, err
        }
        
        // Explanation is automatically logged
        
        return result, nil
    }
    
    return nil, nil
}

func (a *ScalingAgent) ExplainAction(input interface{}, output interface{}) string {
    if a.xaiEngine == nil {
        return "Scaling action performed"
    }
    
    explanation, err := a.xaiEngine.GenerateExplanation(
        a.GetID(),
        a.GetName(),
        "scale",
        input,
        output,
        core.AutoMode,
        0.95,
        "Scaling action",
        nil,
    )
    
    if err != nil {
        return "Unable to generate explanation"
    }
    
    return explanation.Reasoning
}
```

---

## Best Practices

1. **Always Generate Explanations**: Every action should have an explanation
2. **Use Appropriate Confidence Levels**: Auto mode = 95%, Manual mode = 85%
3. **Include Context**: Provide rich context for better explanations
4. **Log Everything**: All explanations should be logged
5. **Chain-of-Thought**: Use CoT reasoning for complex decisions
6. **Alternative Actions**: Always list alternative actions considered

---

## Troubleshooting

### LLM Service Not Available

If LLM reasoning service is unavailable, the system falls back to basic reasoning:

```go
// Fallback is automatic
explanation := xaiEngine.GenerateExplanation(...)
// Will use basic reasoning if LLM fails
```

### Logging Failures

If ELK Stack is unavailable, explanations are logged to files:

```
logs/xai/xai_YYYY-MM-DD.log
```

### Low Confidence

If confidence is below threshold, consider:
- Switching to manual mode
- Requesting user approval
- Gathering more data
- Re-evaluating the decision

---

## Next Steps

1. Integrate XAI into all agents
2. Set up ELK Stack for centralized logging
3. Create dashboard for displaying explanations
4. Add real-time explanation streaming
5. Implement explanation analytics

---

## Related Documentation

- `agents/core/xai.go` - Core XAI implementation
- `agents/core/xai_llm_integration.go` - LLM integration
- `agents/core/xai_logger.go` - Logging implementation
- `agents/core/xai_examples.go` - Usage examples

