# Decision UI - Frontend Interface

## Overview

The Decision UI provides a modern, responsive web interface for displaying and interacting with AI agent decisions. It supports both **Auto Mode** (automatic execution) and **Manual Mode** (user approval required).

## Features

- ✅ **Auto Mode Display**: Shows automatically executed actions with reasoning
- ✅ **Manual Mode Display**: Presents options for user approval
- ✅ **Modern UI**: Clean, responsive design with smooth animations
- ✅ **Real-time Updates**: Supports WebSocket/SSE for live updates
- ✅ **Comprehensive Explanations**: Detailed reasoning and justification
- ✅ **Risk Assessment**: Visual indicators for risk and impact levels

---

## File Structure

```
ui/decision-ui/
├── index.html          # Main HTML structure
├── styles.css          # CSS styling
├── decision-api.js     # API client for backend communication
├── decision-ui.js      # UI controller and logic
└── README.md           # This file
```

---

## Quick Start

### 1. Open in Browser

Simply open `index.html` in a web browser. The UI will load with a demo decision (Auto Mode by default).

### 2. Switch Between Modes

In the browser console, you can switch modes:

```javascript
// Load Auto Mode
loadDecision('auto');

// Load Manual Mode
loadDecision('manual');
```

### 3. Integration with Backend

Update the `DecisionAPI` class in `decision-api.js` to point to your backend:

```javascript
const api = new DecisionAPI('http://your-backend/api/v1/decisions');
```

---

## Components

### Auto Mode UI

**Displays:**
- ✅ Status badge: "Auto Mode"
- ✅ Success indicator: "Action Has Been Automatically Executed"
- ✅ Reasoning card: Detailed explanation of why the action was taken
- ✅ Details card: Agent name, action, confidence, risk, impact, timestamp

**Example:**
```
⚡ Auto Mode

✓ Action Has Been Automatically Executed
"The instance was automatically restarted due to CPU overload."

💡 Reasoning & Explanation
The instance CPU usage has been above 90% for the past 10 minutes...
```

### Manual Mode UI

**Displays:**
- ⚠️ Warning badge: "Manual Mode - Approval Required"
- ⚠️ Error card: Problem description
- 🔍 Analysis card: Reasoning and analysis
- 🎯 Actions card: Available action options with:
  - Description
  - Risk and Impact badges
  - Justification for each action
  - Estimated cost
- ✓ Confirm button: Enabled after selecting an action

**Example:**
```
👤 Manual Mode - Approval Required

⚠️ Issue Detected
CPU usage is at 95% and response times are increasing

🎯 Available Actions
[ ] Scale up from 3 to 5 replicas
    Risk: low | Impact: high
    Reasoning: Adding more replicas will distribute the load...
    Estimated Cost: $15.50

[✓] Confirm Selection
```

---

## API Integration

### DecisionAPI Class

The `DecisionAPI` class handles all backend communication:

```javascript
const api = new DecisionAPI('/api/v1/decisions');

// Get a decision
const decision = await api.getDecision('decision-id');

// Submit user choice (Manual Mode)
const result = await api.submitActionChoice('decision-id', 'option-id');

// Get explanation
const explanation = await api.getExplanation('decision-id', 'detailed');
```

### Expected API Response Format

**Decision Object:**
```json
{
  "mode": "auto" | "manual",
  "agent_id": "self-healing-001",
  "agent_name": "Self-Healing Agent",
  "problem": "EC2 instance is experiencing high CPU usage",
  "reasoning": "Analysis shows...",
  "options": [
    {
      "id": "restart_instance",
      "description": "Restart the EC2 instance",
      "reasoning": "Restarting will clear stuck processes",
      "risk": "low" | "medium" | "high",
      "impact": "low" | "medium" | "high",
      "estimated_cost": 0.0
    }
  ],
  "selected_option": { ... },
  "action_executed": true,
  "execution_result": { ... },
  "explanation": "...",
  "confidence": 0.92,
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
}
```

---

## Styling

### Color Scheme

- **Primary**: Blue (#2563eb)
- **Success**: Green (#10b981) - Auto Mode
- **Warning**: Amber (#f59e0b) - Manual Mode
- **Error**: Red (#ef4444)

### Responsive Design

The UI is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1200px)
- Mobile (< 768px)

---

## Customization

### Change Default Mode

In `decision-ui.js`, modify the initialization:

```javascript
// Load Manual Mode by default
decisionUI.loadDecision('manual', true);
```

### Customize Colors

In `styles.css`, modify CSS variables:

```css
:root {
    --primary-color: #your-color;
    --auto-primary: #your-color;
    --manual-primary: #your-color;
}
```

### Add Custom Actions

Extend the `generateActionOptionHTML` method in `decision-ui.js` to add custom action properties.

---

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Development

### Local Development

1. Open `index.html` in a browser
2. Use browser DevTools for debugging
3. Mock data is provided for testing

### Production Deployment

1. Update API endpoints in `decision-api.js`
2. Configure CORS on backend
3. Deploy to web server (Nginx, Apache, etc.)
4. Or integrate into React/Vue/Angular app

---

## Integration Examples

### React Integration

```jsx
import { useEffect, useState } from 'react';
import { DecisionAPI } from './decision-api';

function DecisionComponent({ decisionId }) {
    const [decision, setDecision] = useState(null);
    const api = new DecisionAPI();

    useEffect(() => {
        api.getDecision(decisionId).then(setDecision);
    }, [decisionId]);

    return (
        <div className="decision-container">
            {/* Render decision UI */}
        </div>
    );
}
```

### Vue Integration

```vue
<template>
    <div class="decision-container">
        <!-- Decision UI -->
    </div>
</template>

<script>
import { DecisionAPI } from './decision-api';

export default {
    data() {
        return {
            decision: null,
            api: new DecisionAPI()
        };
    },
    async mounted() {
        this.decision = await this.api.getDecision(this.decisionId);
    }
};
</script>
```

---

## Next Steps

1. **Backend Integration**: Connect to real API endpoints
2. **WebSocket Support**: Add real-time updates
3. **Authentication**: Add user authentication
4. **History**: Show decision history
5. **Analytics**: Add decision analytics dashboard

---

## License

Part of the AI-Driven Self-Healing Cloud Infrastructure project.

