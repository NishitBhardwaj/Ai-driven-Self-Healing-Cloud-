# Decision Mode System - Auto vs Manual

## Overview

The Decision Mode System provides a dual-mode decision-making framework where agents can operate in either **Auto Mode** (automatic execution) or **Manual Mode** (user approval required). Every decision is accompanied by a comprehensive explanation.

## Features

- ✅ **Auto Mode**: Agents act automatically with post-action explanations
- ✅ **Manual Mode**: Agents present options and wait for user approval
- ✅ **Comprehensive Explanations**: Every decision is fully justified
- ✅ **Risk Assessment**: Built-in risk and impact evaluation
- ✅ **Confidence Scoring**: Confidence levels for all decisions
- ✅ **Configurable**: Per-agent mode configuration

---

## Quick Start

### 1. Basic Usage

```go
import "github.com/ai-driven-self-healing-cloud/agents/core"

// Create a decision handler
handler := core.NewDecisionHandler(core.AutoMode)

// Create a decision
decision := handler.CreateDecision(
    "agent-id",
    "Agent Name",
    "Problem description",
    "Reasoning for the decision",
    []core.ActionOption{
        {
            ID:          "action_id",
            Description: "Action description",
            Reasoning:   "Why this action",
            Risk:        "low",
            Impact:      "high",
        },
    },
)

// Execute the decision
actionExecutor := func(option *core.ActionOption) (interface{}, error) {
    // Execute your action here
    return result, nil
}

err := decision.ExecuteDecision(handler, actionExecutor)
```

### 2. Auto Mode Example

```go
handler := core.NewDecisionHandler(core.AutoMode)

decision := handler.CreateDecision(
    "self-healing-001",
    "Self-Healing Agent",
    "Pod is crashing",
    "Pod has crashed 3 times in 5 minutes",
    []core.ActionOption{
        {
            ID:          "restart_pod",
            Description: "Restart the pod",
            Reasoning:   "Restarting should resolve the crash",
            Risk:        "low",
            Impact:      "medium",
        },
    },
)

decision.SetConfidence(0.9)

// In Auto Mode, the action executes immediately
err := decision.ExecuteDecision(handler, actionExecutor)
```

### 3. Manual Mode Example

```go
handler := core.NewDecisionHandler(core.ManualMode)

// Set up user input callback
handler.UserInputCallback = func(decision *core.AgentDecision) (string, error) {
    // Present options to user and get their choice
    // Return the selected option ID
    return "restart_pod", nil
}

decision := handler.CreateDecision(
    "security-001",
    "Security Agent",
    "Suspicious activity detected",
    "Multiple failed login attempts",
    []core.ActionOption{
        {
            ID:          "block_ip",
            Description: "Block the IP address",
            Risk:        "low",
            Impact:      "high",
        },
        {
            ID:          "investigate",
            Description: "Investigate further",
            Risk:        "medium",
            Impact:      "low",
        },
    },
)

// In Manual Mode, waits for user input before executing
err := decision.ExecuteDecision(handler, actionExecutor)
```

---

## Components

### 1. DecisionHandler

Manages decision execution and user interaction.

```go
type DecisionHandler struct {
    DefaultMode                Mode
    UserInputCallback         func(*AgentDecision) (string, error)
    NotificationCallback      func(*AgentDecision) error
    ApprovalRequiredForActions []string
}
```

### 2. AgentDecision

Represents a decision made by an agent.

```go
type AgentDecision struct {
    Mode            Mode
    AgentID         string
    Problem         string
    Reasoning       string
    Options         []ActionOption
    SelectedOption  *ActionOption
    ActionExecuted  bool
    Explanation     string
    Confidence      float64
    // ... more fields
}
```

### 3. ActionOption

Represents a possible action.

```go
type ActionOption struct {
    ID            string
    Description   string
    Reasoning     string
    Risk          string  // "low", "medium", "high"
    Impact        string  // "low", "medium", "high"
    EstimatedCost float64
}
```

---

## Explainability Layer

### Generate Explanations

```go
explainEngine := core.NewExplainabilityEngine()
explanation := explainEngine.GenerateExplanation(decision, core.DetailedExplanation)

// Get human-readable text
text := explanation.ToHumanReadable()
fmt.Println(text)

// Get JSON format
jsonData, _ := explanation.ToJSON()
```

### Explanation Levels

- **BriefExplanation**: Concise summary
- **DetailedExplanation**: Comprehensive details
- **TechnicalExplanation**: Technical details for developers

### Explanation Contents

- Problem description
- Analysis and reasoning
- Options evaluated
- Selected option justification
- Reasoning chain (step-by-step)
- Confidence factors
- Risk assessment
- Expected outcome
- Alternative actions

---

## Configuration

### Load Configuration

```go
config, err := core.LoadDecisionConfig("config/decision_config.json")
if err != nil {
    config = core.DefaultDecisionConfig()
}
```

### Default Configuration

```json
{
  "default_mode": "auto",
  "agent_modes": {
    "self-healing": "auto",
    "scaling": "auto",
    "security": "manual",
    "coding": "manual",
    "monitoring": "auto"
  },
  "auto_approve_actions": [
    "restart_pod",
    "scale_up",
    "collect_metrics"
  ],
  "require_approval_for_actions": [
    "delete",
    "rebuild",
    "rollback",
    "code_change"
  ],
  "confidence_threshold": 0.7,
  "notification_enabled": true,
  "explanation_level": "detailed"
}
```

### Per-Agent Mode

```go
config.SetModeForAgent("security", core.ManualMode)
mode := config.GetModeForAgent("security") // Returns ManualMode
```

---

## Integration with Agents

### Example: Self-Healing Agent

```go
func (h *Healer) Heal(request *HealingRequest) (*HealingResult, error) {
    // Create decision handler
    handler := core.NewDecisionHandler(core.AutoMode)
    
    // Determine healing options
    options := []core.ActionOption{
        {
            ID:          "restart_pod",
            Description: "Restart the pod",
            Reasoning:   "Pod is in crash loop",
            Risk:        "low",
            Impact:      "medium",
        },
    }
    
    // Create decision
    decision := handler.CreateDecision(
        h.GetID(),
        h.GetName(),
        request.Error,
        "Pod failure detected, restarting should resolve",
        options,
    )
    
    // Execute
    actionExecutor := func(option *core.ActionOption) (interface{}, error) {
        // Execute actual healing action
        return h.executeHealingAction(option.ID, request)
    }
    
    err := decision.ExecuteDecision(handler, actionExecutor)
    if err != nil {
        return nil, err
    }
    
    // Generate explanation
    explainEngine := core.NewExplainabilityEngine()
    explanation := explainEngine.GenerateExplanation(decision, core.DetailedExplanation)
    
    // Return result with explanation
    return &HealingResult{
        Success:   decision.ActionExecuted,
        Reasoning: explanation.ToHumanReadable(),
    }, nil
}
```

---

## Auto vs Manual Mode Behavior

### Auto Mode

1. Agent detects issue
2. Agent analyzes and generates options
3. Agent automatically selects best option
4. Action executes immediately
5. User receives notification with explanation

### Manual Mode

1. Agent detects issue
2. Agent analyzes and generates options
3. Agent presents options to user
4. User selects action
5. Action executes after approval
6. User receives explanation

---

## Risk and Impact Assessment

### Risk Levels

- **low**: Minimal risk, safe to execute
- **medium**: Moderate risk, should be reviewed
- **high**: High risk, requires careful consideration

### Impact Levels

- **low**: Minimal impact on system
- **medium**: Moderate impact on system
- **high**: Significant impact on system

### Automatic Selection

In Auto Mode, the system automatically selects the best option based on:
- Risk level (lower is better)
- Impact level (higher is better for positive impact)
- Estimated cost (lower is better)
- Confidence score (higher is better)

---

## Notification System

### Setup Notifications

```go
handler.NotificationCallback = func(decision *core.AgentDecision) error {
    // Send notification via email, Slack, etc.
    return sendNotification(decision)
}
```

### Notification Contents

- Agent name
- Problem description
- Selected action
- Reasoning
- Execution result
- Explanation

---

## Best Practices

1. **Use Auto Mode for**: Low-risk, high-confidence actions (restart pods, scale up)
2. **Use Manual Mode for**: High-risk actions (deletions, rollbacks, code changes)
3. **Set Confidence Thresholds**: Only auto-execute if confidence > 0.7
4. **Provide Clear Options**: Always include reasoning for each option
5. **Generate Explanations**: Always generate explanations for transparency
6. **Monitor Actions**: Track all decisions for learning and improvement

---

## API Reference

See the code documentation in:
- `decision_mode.go` - Core decision mode logic
- `explainability.go` - Explanation generation
- `decision_config.go` - Configuration management
- `decision_mode_example.go` - Usage examples

---

## Next Steps

- Integrate with all agents
- Add UI for manual mode interactions
- Implement notification channels (email, Slack, etc.)
- Add decision history and analytics
- Implement learning from user feedback

