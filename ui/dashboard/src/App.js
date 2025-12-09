import React, { useState, useEffect } from 'react';
import { Container, Box, Grid, Paper, Typography, Tabs, Tab } from '@mui/material';
import DashboardOverview from './components/DashboardOverview';
import AgentStatusCards from './components/AgentStatusCards';
import SystemHealthChart from './components/SystemHealthChart';
import LogTable from './components/LogTable';
import ManualModeUI from './components/ManualModeUI';
import AutoModeNotifications from './components/AutoModeNotifications';
import ModeToggle from './components/ModeToggle';
import EventHistoryTimeline from './components/EventHistoryTimeline';
import PushNotifications from './components/PushNotifications';
import { useWebSocket } from './hooks/useWebSocket';
import { getWebSocketService } from './services/websocketService';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [systemMode, setSystemMode] = useState('auto');
  const [agents, setAgents] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [pendingDecisions, setPendingDecisions] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // WebSocket connection for real-time updates
  const { connected, data } = useWebSocket('ws://localhost:8080/ws');
  
  // Initialize WebSocket service
  useEffect(() => {
    const wsService = getWebSocketService('ws://localhost:8080/ws');
    if (!wsService.isConnected) {
      wsService.connect();
    }
    return () => {
      // Service will handle cleanup
    };
  }, []);

  useEffect(() => {
    if (data) {
      // Handle different types of WebSocket messages
      switch (data.type) {
        case 'agent_update':
          setAgents(prev => updateAgents(prev, data.payload));
          break;
        case 'system_health':
          setSystemHealth(data.payload);
          break;
        case 'log_entry':
          setLogs(prev => [data.payload, ...prev].slice(0, 1000)); // Keep last 1000 logs
          break;
        case 'decision_pending':
          setPendingDecisions(prev => [...prev, data.payload]);
          break;
        case 'decision_executed':
          setNotifications(prev => [data.payload, ...prev].slice(0, 50)); // Keep last 50 notifications
          setPendingDecisions(prev => prev.filter(d => d.id !== data.payload.decision_id));
          break;
        default:
          break;
      }
    }
  }, [data]);

  const updateAgents = (prevAgents, update) => {
    const index = prevAgents.findIndex(a => a.id === update.id);
    if (index >= 0) {
      const updated = [...prevAgents];
      updated[index] = { ...updated[index], ...update };
      return updated;
    }
    return [...prevAgents, update];
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleModeChange = (newMode) => {
    setSystemMode(newMode);
    // Send mode change to backend
    if (connected) {
      // WebSocket message would be sent here
    }
  };

  const handleDecisionConfirm = (decisionId, optionId) => {
    // Send confirmation to backend
    fetch(`/api/v1/decisions/${decisionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ option_id: optionId }),
    })
      .then(res => res.json())
      .then(data => {
        setPendingDecisions(prev => prev.filter(d => d.id !== decisionId));
        setNotifications(prev => [data, ...prev].slice(0, 50));
      })
      .catch(err => console.error('Error confirming decision:', err));
  };

  return (
    <Container maxWidth="xl" className="app-container">
      <Box sx={{ my: 4 }}>
        {/* Header */}
        <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item>
              <Typography variant="h4" component="h1" sx={{ color: 'white', fontWeight: 'bold' }}>
                🤖 AI Agent Dashboard
              </Typography>
              <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                Real-time Explainability & System Monitoring
              </Typography>
            </Grid>
            <Grid item>
              <ModeToggle mode={systemMode} onModeChange={handleModeChange} />
            </Grid>
          </Grid>
        </Paper>

        {/* Connection Status */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 12,
              height: 12,
              borderRadius: '50%',
              bgcolor: connected ? 'success.main' : 'error.main',
            }}
          />
          <Typography variant="body2" color="text.secondary">
            {connected ? 'Connected' : 'Disconnected'} to WebSocket
          </Typography>
        </Box>

        {/* Tabs */}
        <Paper elevation={2} sx={{ mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
            <Tab label="Overview" />
            <Tab label="Agents" />
            <Tab label="System Health" />
            <Tab label="Logs" />
            <Tab label="Event History" />
            <Tab label={systemMode === 'manual' ? 'Pending Decisions' : 'Notifications'} />
          </Tabs>
        </Paper>

        {/* Tab Content */}
        <Box>
          {activeTab === 0 && (
            <DashboardOverview
              agents={agents}
              systemHealth={systemHealth}
              systemMode={systemMode}
            />
          )}
          {activeTab === 1 && (
            <AgentStatusCards agents={agents} />
          )}
          {activeTab === 2 && (
            <SystemHealthChart data={systemHealth} />
          )}
          {activeTab === 3 && (
            <LogTable logs={logs} />
          )}
          {activeTab === 4 && (
            <EventHistoryTimeline />
          )}
          {activeTab === 5 && (
            systemMode === 'manual' ? (
              <ManualModeUI
                pendingDecisions={pendingDecisions}
                onConfirm={handleDecisionConfirm}
              />
            ) : (
              <AutoModeNotifications notifications={notifications} />
            )
          )}
        </Box>
        
        {/* Push Notifications - Always visible */}
        <PushNotifications />
      </Box>
    </Container>
  );
}

export default App;

