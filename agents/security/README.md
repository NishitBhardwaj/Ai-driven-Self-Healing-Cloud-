# Security Agent

## Purpose

The Security Agent is responsible for:
- Detecting security threats and intrusions
- Validating IAM and security policies
- Detecting API abuse patterns
- Providing security recommendations

## Responsibilities

1. **Threat Detection**: Identifies security threats in logs and traffic
2. **Policy Validation**: Validates IAM and security policies
3. **Anomaly Detection**: Detects unusual patterns indicating attacks
4. **Security Recommendations**: Provides actionable security advice

## Functions

- `detect_intrusion()` - Detect intrusion attempts
- `validate_policy()` - Validate security policies
- `llm_call()` - Make LLM API calls for analysis

## Input

- Security logs
- Network traffic data
- IAM policies
- API access patterns

## Output

- Detected threats with severity
- Policy validation results
- Security recommendations

## LLM Integration

Uses shared `llm.py` module supporting:
- OpenRouter (default)
- Google Gemini

## Usage

```python
from agent import SecurityAgent

agent = SecurityAgent()
agent.start()

# Detect intrusion
threats = agent.detect_intrusion(logs)

# Validate policy
validation = agent.validate_policy(policy, "iam")
```

