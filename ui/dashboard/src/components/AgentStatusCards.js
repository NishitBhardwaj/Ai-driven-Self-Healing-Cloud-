import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Chip,
  Card,
  CardContent,
  CardActions,
  Button,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Info,
  PlayArrow,
  Stop,
  Refresh,
} from '@mui/icons-material';
import { format } from 'date-fns';

/**
 * Agent Status Cards Component
 * Displays status cards for each agent with last action and confidence level
 */
function AgentStatusCards({ agents }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <CheckCircle color="success" />;
      case 'stopped':
        return <Stop color="error" />;
      case 'error':
        return <Error color="error" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'error';
      case 'error':
        return 'error';
      default:
        return 'warning';
    }
  };

  const defaultAgents = [
    {
      id: 'self-healing-001',
      name: 'Self-Healing Agent',
      status: 'running',
      lastAction: 'restart_pod',
      lastActionExplanation: 'Pod was restarted due to crash loop detection',
      confidence: 0.95,
      mode: 'auto',
      lastUpdate: new Date(),
    },
    {
      id: 'scaling-001',
      name: 'Scaling Agent',
      status: 'running',
      lastAction: 'scale_up',
      lastActionExplanation: 'Scaled up from 3 to 5 replicas due to high CPU usage',
      confidence: 0.85,
      mode: 'manual',
      lastUpdate: new Date(),
    },
    {
      id: 'security-001',
      name: 'Security Agent',
      status: 'running',
      lastAction: 'block_ip',
      lastActionExplanation: 'Blocked suspicious IP address after multiple failed login attempts',
      confidence: 0.92,
      mode: 'auto',
      lastUpdate: new Date(),
    },
    {
      id: 'monitoring-001',
      name: 'Monitoring Agent',
      status: 'running',
      lastAction: 'collect_metrics',
      lastActionExplanation: 'Collected system metrics and updated health status',
      confidence: 0.98,
      mode: 'auto',
      lastUpdate: new Date(),
    },
  ];

  const displayAgents = agents.length > 0 ? agents : defaultAgents;

  return (
    <Grid container spacing={3}>
      {displayAgents.map((agent) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
          <Card elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              {/* Agent Header */}
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" component="h3">
                  {agent.name}
                </Typography>
                {getStatusIcon(agent.status)}
              </Box>

              {/* Status Chip */}
              <Chip
                label={agent.status}
                color={getStatusColor(agent.status)}
                size="small"
                sx={{ mb: 2 }}
              />

              {/* Last Action */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Last Action
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {agent.lastAction || 'No action'}
                </Typography>
                {agent.lastActionExplanation && (
                  <Tooltip title={agent.lastActionExplanation} arrow>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {agent.lastActionExplanation}
                    </Typography>
                  </Tooltip>
                )}
              </Box>

              {/* Confidence Level */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Confidence
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {(agent.confidence * 100).toFixed(0)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={agent.confidence * 100}
                  color={agent.confidence >= 0.9 ? 'success' : agent.confidence >= 0.7 ? 'warning' : 'error'}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              {/* Mode */}
              <Chip
                label={agent.mode === 'auto' ? 'Auto Mode' : 'Manual Mode'}
                color={agent.mode === 'auto' ? 'success' : 'warning'}
                size="small"
                sx={{ mb: 1 }}
              />

              {/* Last Update */}
              {agent.lastUpdate && (
                <Typography variant="caption" color="text.secondary">
                  Updated: {format(new Date(agent.lastUpdate), 'HH:mm:ss')}
                </Typography>
              )}
            </CardContent>

            <CardActions>
              <Button size="small" startIcon={<Info />}>
                Details
              </Button>
              <Button size="small" startIcon={<Refresh />}>
                Refresh
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default AgentStatusCards;

