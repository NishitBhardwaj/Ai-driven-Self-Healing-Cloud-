# AI Agent Dashboard - Real-time Explainability UI

## Overview

A modern React dashboard for monitoring AI agents, system health, and real-time explainability. Built with Material UI, Chart.js, and WebSocket integration for live updates.

## Features

- ✅ **Dashboard Overview**: System health, active agents, resource usage
- ✅ **Agent Status Cards**: Real-time agent status with last action and confidence
- ✅ **System Health Charts**: Visual performance metrics using Chart.js
- ✅ **Log Table**: Real-time logs with filtering and explanations
- ✅ **Auto Mode UI**: Notifications for automatic actions with explanations
- ✅ **Manual Mode UI**: Error details and action approval interface
- ✅ **WebSocket Integration**: Real-time data updates
- ✅ **Mode Toggle**: Switch between Auto and Manual modes

## Installation

```bash
cd ui/dashboard
npm install
```

## Running the Dashboard

```bash
npm start
```

The dashboard will open at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

## Project Structure

```
ui/dashboard/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── DashboardOverview.js      # Main overview dashboard
│   │   ├── AgentStatusCards.js       # Agent status cards
│   │   ├── SystemHealthChart.js      # Health metrics charts
│   │   ├── LogTable.js               # Log table with filtering
│   │   ├── ManualModeUI.js           # Manual mode interface
│   │   ├── AutoModeNotifications.js  # Auto mode notifications
│   │   └── ModeToggle.js             # Mode toggle component
│   ├── hooks/
│   │   └── useWebSocket.js           # WebSocket hook
│   ├── App.js                         # Main app component
│   ├── App.css                        # App styles
│   ├── index.js                       # Entry point
│   └── index.css                      # Global styles
├── package.json
└── README.md
```

## Components

### DashboardOverview
Displays overall system health, active agents count, system mode, and resource usage metrics (CPU, Memory, Error Rate, Latency).

### AgentStatusCards
Shows status cards for each agent with:
- Agent status (Running/Stopped)
- Last action taken
- Action explanation
- Confidence level
- Mode (Auto/Manual)

### SystemHealthChart
Visualizes system health metrics using Chart.js:
- Line chart for historical data (CPU, Memory, Error Rate)
- Bar chart for current resource usage

### LogTable
Displays real-time logs with:
- Timestamp
- Agent name
- Action
- Explanation (with tooltip)
- Confidence level
- Mode
- Type (info/success/warning/error)
- Filtering by agent and type

### ManualModeUI
Shows pending decisions requiring user approval:
- Error/problem details
- Available actions with reasoning
- Risk and impact badges
- Estimated cost
- Confirm button

### AutoModeNotifications
Displays notifications for automatic actions:
- Action executed message
- Explanation (collapsible)
- Confidence level
- Timestamp

### ModeToggle
Allows switching between Auto and Manual modes.

## WebSocket Integration

The dashboard connects to a WebSocket server at `ws://localhost:8080/ws` for real-time updates.

### Message Types

- `agent_update`: Agent status updates
- `system_health`: System health metrics
- `log_entry`: New log entries
- `decision_pending`: Pending decisions (Manual Mode)
- `decision_executed`: Executed decisions (Auto Mode)

## API Integration

The dashboard expects the following API endpoints:

- `GET /api/v1/agents`: Get all agents
- `GET /api/v1/system/health`: Get system health
- `GET /api/v1/logs`: Get logs
- `POST /api/v1/decisions/:id/approve`: Approve decision (Manual Mode)

## Configuration

Update WebSocket URL in `src/hooks/useWebSocket.js`:

```javascript
const { connected, data } = useWebSocket('ws://your-backend:8080/ws');
```

## Dependencies

- **React 18**: UI framework
- **Material UI 5**: Component library
- **Chart.js 4**: Charting library
- **React Table 7**: Table component
- **Socket.io Client**: WebSocket client
- **date-fns**: Date formatting
- **Axios**: HTTP client

## Development

### Adding New Components

1. Create component in `src/components/`
2. Import and use in `App.js`
3. Add to appropriate tab

### Styling

- Material UI theme in `src/index.js`
- Component styles in `src/App.css`
- Global styles in `src/index.css`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Next Steps

1. Connect to real backend API
2. Configure WebSocket server
3. Add authentication
4. Add user preferences
5. Add export functionality
6. Add advanced filtering

