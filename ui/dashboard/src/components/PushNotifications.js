import React, { useState, useEffect, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Box,
  IconButton,
  Collapse,
  Typography,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Error,
  Warning,
  Info,
  ExpandMore,
  ExpandLess,
  Notifications,
  NotificationsActive,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { getWebSocketService } from '../services/websocketService';

/**
 * Push Notifications Component
 * Real-time notifications for agent actions, errors, and resolved tasks
 */
function PushNotifications() {
  const [notifications, setNotifications] = useState([]);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [currentNotification, setCurrentNotification] = useState(null);
  const [notificationHistory, setNotificationHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const wsService = getWebSocketService();

  useEffect(() => {
    // Subscribe to notification events
    const unsubscribeAgentAction = wsService.on('agent_action', handleNotification);
    const unsubscribeDecisionExecuted = wsService.on('decision_executed', handleNotification);
    const unsubscribeErrorDetected = wsService.on('error_detected', handleNotification);
    const unsubscribeTaskResolved = wsService.on('task_resolved', handleNotification);
    const unsubscribeProblemDetected = wsService.on('problem_detected', handleNotification);

    return () => {
      unsubscribeAgentAction();
      unsubscribeDecisionExecuted();
      unsubscribeErrorDetected();
      unsubscribeTaskResolved();
      unsubscribeProblemDetected();
    };
  }, []);

  const handleNotification = useCallback((event) => {
    const notification = createNotification(event);
    
    // Add to history
    setNotificationHistory(prev => [notification, ...prev].slice(0, 100));

    // Show immediate notification
    setCurrentNotification(notification);
    setOpenSnackbar(true);

    // Auto-hide after delay (except errors)
    if (notification.severity !== 'error') {
      setTimeout(() => {
        setOpenSnackbar(false);
      }, notification.duration || 5000);
    }
  }, []);

  const createNotification = (event) => {
    const { type, payload } = event;
    
    let severity = 'info';
    let title = 'Notification';
    let message = 'An event occurred';
    let duration = 5000;

    switch (type) {
      case 'agent_action':
        severity = 'success';
        title = `${payload.agent_name || 'Agent'} Action`;
        message = payload.explanation || `Action: ${payload.action || 'executed'}`;
        break;
      case 'decision_executed':
        severity = payload.mode === 'auto' ? 'success' : 'info';
        title = 'Decision Executed';
        message = payload.explanation || 'A decision has been executed';
        break;
      case 'error_detected':
        severity = 'error';
        title = 'Error Detected';
        message = payload.error || payload.problem || 'An error has been detected';
        duration = 10000; // Errors stay longer
        break;
      case 'task_resolved':
        severity = 'success';
        title = 'Task Resolved';
        message = payload.message || 'A task has been successfully resolved';
        break;
      case 'problem_detected':
        severity = 'warning';
        title = 'Problem Detected';
        message = payload.problem || 'A problem has been detected';
        if (payload.mode === 'manual') {
          message += ' - Action approval required';
        }
        duration = 8000;
        break;
      default:
        title = getEventTypeLabel(type);
        message = payload.message || payload.explanation || 'Event occurred';
    }

    return {
      id: event.id || `notif-${Date.now()}`,
      type,
      severity,
      title,
      message,
      duration,
      timestamp: event.timestamp || new Date().toISOString(),
      payload,
      agentName: payload?.agent_name || payload?.agentName,
      action: payload?.action || payload?.action_taken,
      confidence: payload?.confidence || payload?.confidence_level,
    };
  };

  const getEventTypeLabel = (type) => {
    const labels = {
      'agent_action': 'Agent Action',
      'decision_executed': 'Decision Executed',
      'error_detected': 'Error Detected',
      'task_resolved': 'Task Resolved',
      'problem_detected': 'Problem Detected',
    };
    return labels[type] || type;
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'success':
        return <CheckCircle />;
      case 'error':
        return <Error />;
      case 'warning':
        return <Warning />;
      default:
        return <Info />;
    }
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleCloseNotification = (notificationId) => {
    setNotificationHistory(prev => prev.filter(n => n.id !== notificationId));
  };

  return (
    <>
      {/* Notification History Button */}
      <Box sx={{ position: 'fixed', top: 80, right: 20, zIndex: 1300 }}>
        <IconButton
          color="primary"
          onClick={() => setShowHistory(!showHistory)}
          sx={{
            bgcolor: 'background.paper',
            boxShadow: 3,
            '&:hover': { bgcolor: 'action.hover' },
          }}
        >
          {showHistory ? <NotificationsActive /> : <Notifications />}
          {notificationHistory.length > 0 && (
            <Chip
              label={notificationHistory.length}
              size="small"
              color="error"
              sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                height: 20,
                minWidth: 20,
                fontSize: '0.7rem',
              }}
            />
          )}
        </IconButton>
      </Box>

      {/* Notification History Panel */}
      <Collapse in={showHistory} orientation="horizontal">
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            top: 120,
            right: 20,
            width: 400,
            maxHeight: '70vh',
            zIndex: 1300,
            overflow: 'auto',
          }}
        >
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Notification History</Typography>
            <IconButton size="small" onClick={() => setShowHistory(false)}>
              <Close />
            </IconButton>
          </Box>
          <Divider />
          <List>
            {notificationHistory.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="No notifications"
                  secondary="Notifications will appear here as they occur"
                />
              </ListItem>
            ) : (
              notificationHistory.map((notification) => (
                <React.Fragment key={notification.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getSeverityIcon(notification.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                          <Typography variant="subtitle2">{notification.title}</Typography>
                          <IconButton
                            size="small"
                            onClick={() => handleCloseNotification(notification.id)}
                          >
                            <Close fontSize="small" />
                          </IconButton>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {notification.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(notification.timestamp), 'HH:mm:ss')}
                          </Typography>
                          {notification.agentName && (
                            <Chip
                              label={notification.agentName}
                              size="small"
                              sx={{ mt: 0.5, mr: 0.5 }}
                            />
                          )}
                          {notification.confidence && (
                            <Chip
                              label={`${(notification.confidence * 100).toFixed(0)}%`}
                              size="small"
                              color={notification.confidence >= 0.9 ? 'success' : 'warning'}
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))
            )}
          </List>
        </Paper>
      </Collapse>

      {/* Real-time Snackbar Notifications */}
      {currentNotification && (
        <Snackbar
          open={openSnackbar}
          autoHideDuration={currentNotification.duration}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          sx={{ mt: 8 }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity={currentNotification.severity}
            variant="filled"
            sx={{ width: '100%', minWidth: 400 }}
            icon={getSeverityIcon(currentNotification.severity)}
          >
            <AlertTitle>{currentNotification.title}</AlertTitle>
            {currentNotification.message}
            {currentNotification.agentName && (
              <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label={currentNotification.agentName} size="small" />
                {currentNotification.confidence && (
                  <Chip
                    label={`${(currentNotification.confidence * 100).toFixed(0)}% confidence`}
                    size="small"
                    color={currentNotification.confidence >= 0.9 ? 'success' : 'warning'}
                  />
                )}
              </Box>
            )}
          </Alert>
        </Snackbar>
      )}
    </>
  );
}

export default PushNotifications;

