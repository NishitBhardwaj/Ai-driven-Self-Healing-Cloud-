import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  CheckCircle,
  Info,
  ExpandMore,
  ExpandLess,
  Notifications,
} from '@mui/icons-material';
import { format } from 'date-fns';

/**
 * Auto Mode Notifications Component
 * Displays notifications when actions are automatically taken
 */
function AutoModeNotifications({ notifications }) {
  const [expanded, setExpanded] = React.useState({});

  const sampleNotifications = notifications.length > 0 ? notifications : [
    {
      id: 'notif-1',
      agent_name: 'Self-Healing Agent',
      action: 'restart_pod',
      message: 'The instance was automatically restarted.',
      explanation: 'CPU usage exceeded threshold. The instance was restarted to prevent service disruption.',
      confidence: 0.95,
      timestamp: new Date(Date.now() - 5 * 60000),
      status: 'success',
    },
    {
      id: 'notif-2',
      agent_name: 'Scaling Agent',
      action: 'scale_up',
      message: 'Service scaled up automatically.',
      explanation: 'Detected sustained high CPU usage (95%) for 10 minutes. Scaled from 3 to 5 replicas to distribute load.',
      confidence: 0.92,
      timestamp: new Date(Date.now() - 15 * 60000),
      status: 'success',
    },
    {
      id: 'notif-3',
      agent_name: 'Security Agent',
      action: 'block_ip',
      message: 'Suspicious IP address blocked.',
      explanation: 'Multiple failed login attempts detected from IP 192.168.1.100. Blocked to prevent potential security breach.',
      confidence: 0.88,
      timestamp: new Date(Date.now() - 30 * 60000),
      status: 'success',
    },
  ];

  const handleExpand = (id) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  if (sampleNotifications.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Notifications sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No Recent Notifications
        </Typography>
        <Typography variant="body2" color="text.secondary">
          All systems are operating normally. No automatic actions have been taken recently.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 2, mb: 2, bgcolor: 'info.light', color: 'info.contrastText' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Info />
          <Typography variant="body2">
            In Auto Mode, agents automatically take actions and notify you with explanations.
          </Typography>
        </Box>
      </Paper>

      <List>
        {sampleNotifications.map((notification, index) => (
          <React.Fragment key={notification.id}>
            <Card elevation={2} sx={{ mb: 2 }}>
              <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <CheckCircle color={getStatusColor(notification.status)} />
                      <Typography variant="h6">{notification.agent_name}</Typography>
                      <Chip
                        label={notification.action}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {format(new Date(notification.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={`${(notification.confidence * 100).toFixed(0)}% Confidence`}
                      color={notification.confidence >= 0.9 ? 'success' : 'warning'}
                      size="small"
                    />
                    <IconButton
                      size="small"
                      onClick={() => handleExpand(notification.id)}
                    >
                      {expanded[notification.id] ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                  </Box>
                </Box>

                {/* Message */}
                <Alert severity={getStatusColor(notification.status)} sx={{ mb: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Action Executed
                  </Typography>
                  <Typography variant="body2">{notification.message}</Typography>
                </Alert>

                {/* Explanation (Collapsible) */}
                <Collapse in={expanded[notification.id]}>
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Explanation
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {notification.explanation}
                    </Typography>
                  </Box>
                </Collapse>
              </CardContent>
            </Card>
            {index < sampleNotifications.length - 1 && <Divider />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
}

export default AutoModeNotifications;

