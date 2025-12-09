import React, { useState, useEffect, useMemo } from 'react';
import {
  Paper,
  Typography,
  Box,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  Chip,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Error,
  Warning,
  Info,
  Healing,
  TrendingUp,
  Security,
  Code,
  Monitor,
  FilterList,
  Refresh,
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import { getWebSocketService } from '../services/websocketService';

/**
 * Event History Timeline Component
 * Displays a timeline of all events: task creation, error detection, healing actions, scaling actions
 */
function EventHistoryTimeline() {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState({ type: 'all', agent: 'all' });
  const [expandedEvents, setExpandedEvents] = useState({});

  const wsService = getWebSocketService();

  useEffect(() => {
    // Load initial event history
    const history = wsService.getEventHistory({ limit: 100 });
    setEvents(history);

    // Subscribe to new events
    const unsubscribe = wsService.on('*', (event) => {
      setEvents(prev => [event, ...prev].slice(0, 500)); // Keep last 500 events
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const getEventIcon = (type) => {
    switch (type) {
      case 'agent_action':
      case 'healing_action':
        return <Healing color="success" />;
      case 'scaling_action':
        return <TrendingUp color="primary" />;
      case 'error_detected':
      case 'error':
        return <Error color="error" />;
      case 'security_alert':
      case 'security_action':
        return <Security color="warning" />;
      case 'code_action':
      case 'code_fix':
        return <Code color="info" />;
      case 'monitoring':
      case 'metrics_update':
        return <Monitor color="info" />;
      case 'task_created':
        return <Info color="info" />;
      default:
        return <Info color="action" />;
    }
  };

  const getEventColor = (type, status) => {
    if (status === 'error' || type === 'error_detected') return 'error';
    if (status === 'success' || type === 'healing_action' || type === 'scaling_action') return 'success';
    if (status === 'warning' || type === 'security_alert') return 'warning';
    return 'info';
  };

  const getEventTypeLabel = (type) => {
    const labels = {
      'agent_action': 'Agent Action',
      'healing_action': 'Healing Action',
      'scaling_action': 'Scaling Action',
      'error_detected': 'Error Detected',
      'security_alert': 'Security Alert',
      'code_action': 'Code Action',
      'monitoring': 'Monitoring',
      'task_created': 'Task Created',
      'decision_executed': 'Decision Executed',
      'decision_pending': 'Decision Pending',
    };
    return labels[type] || type;
  };

  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      if (filter.type !== 'all' && event.type !== filter.type) return false;
      if (filter.agent !== 'all') {
        const agentId = event.payload?.agent_id || event.payload?.agentId;
        if (agentId !== filter.agent) return false;
      }
      return true;
    });
  }, [events, filter]);

  const uniqueEventTypes = useMemo(() => {
    return [...new Set(events.map(e => e.type))];
  }, [events]);

  const uniqueAgents = useMemo(() => {
    const agents = new Set();
    events.forEach(event => {
      const agentId = event.payload?.agent_id || event.payload?.agentId;
      const agentName = event.payload?.agent_name || event.payload?.agentName;
      if (agentId) {
        agents.add(JSON.stringify({ id: agentId, name: agentName || agentId }));
      }
    });
    return Array.from(agents).map(s => JSON.parse(s));
  }, [events]);

  const handleExpand = (eventId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId],
    }));
  };

  const handleRefresh = () => {
    const history = wsService.getEventHistory({ limit: 100 });
    setEvents(history);
  };

  if (filteredEvents.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <Info sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No Events Found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {events.length === 0
            ? 'No events have been recorded yet. Events will appear here as they occur.'
            : 'No events match the selected filters.'}
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Filters */}
      <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <FilterList color="action" />
          <TextField
            select
            label="Event Type"
            value={filter.type}
            onChange={(e) => setFilter(prev => ({ ...prev, type: e.target.value }))}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="all">All Types</MenuItem>
            {uniqueEventTypes.map(type => (
              <MenuItem key={type} value={type}>
                {getEventTypeLabel(type)}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Agent"
            value={filter.agent}
            onChange={(e) => setFilter(prev => ({ ...prev, agent: e.target.value }))}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="all">All Agents</MenuItem>
            {uniqueAgents.map(agent => (
              <MenuItem key={agent.id} value={agent.id}>
                {agent.name}
              </MenuItem>
            ))}
          </TextField>
          <Box sx={{ flexGrow: 1 }} />
          <IconButton onClick={handleRefresh} title="Refresh">
            <Refresh />
          </IconButton>
          <Typography variant="body2" color="text.secondary">
            {filteredEvents.length} event{filteredEvents.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
      </Paper>

      {/* Timeline */}
      <Paper elevation={3} sx={{ p: 3, maxHeight: '80vh', overflow: 'auto' }}>
        <Timeline>
          {filteredEvents.map((event, index) => {
            const isExpanded = expandedEvents[event.id];
            const status = event.payload?.status || event.payload?.type || 'info';
            const color = getEventColor(event.type, status);
            const agentName = event.payload?.agent_name || event.payload?.agentName || 'Unknown Agent';
            const action = event.payload?.action || event.payload?.action_taken || 'Action';
            const explanation = event.payload?.explanation || event.payload?.reasoning || 'No explanation available';
            const confidence = event.payload?.confidence || event.payload?.confidence_level;

            return (
              <TimelineItem key={event.id}>
                <TimelineOppositeContent sx={{ flex: 0.3, pt: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    {format(new Date(event.timestamp), 'HH:mm:ss')}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                  </Typography>
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot color={color}>
                    {getEventIcon(event.type)}
                  </TimelineDot>
                  {index < filteredEvents.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent sx={{ py: 2 }}>
                  <Card elevation={2}>
                    <CardContent>
                      {/* Event Header */}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {getEventTypeLabel(event.type)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {agentName}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                          {confidence && (
                            <Chip
                              label={`${(confidence * 100).toFixed(0)}%`}
                              size="small"
                              color={confidence >= 0.9 ? 'success' : 'warning'}
                            />
                          )}
                          <Chip
                            label={status}
                            size="small"
                            color={color}
                          />
                        </Box>
                      </Box>

                      {/* Action */}
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 'medium' }}>
                        {action}
                      </Typography>

                      {/* Explanation (Collapsible) */}
                      <Accordion expanded={isExpanded} onChange={() => handleExpand(event.id)}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="caption" color="text.secondary">
                            {isExpanded ? 'Hide' : 'Show'} Explanation
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                            {explanation}
                          </Typography>
                          {event.payload?.reasoning_chain && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="subtitle2" gutterBottom>
                                Reasoning Chain:
                              </Typography>
                              {event.payload.reasoning_chain.map((step, idx) => (
                                <Box key={idx} sx={{ mb: 1, pl: 2, borderLeft: 2, borderColor: 'divider' }}>
                                  <Typography variant="caption" fontWeight="bold">
                                    Step {step.step_number || idx + 1}: {step.description || 'Step'}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary" display="block">
                                    {step.reasoning}
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          )}
                        </AccordionDetails>
                      </Accordion>

                      {/* Additional Details */}
                      {event.payload && (
                        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {event.payload.mode && (
                            <Chip
                              label={event.payload.mode === 'auto' ? 'Auto Mode' : 'Manual Mode'}
                              size="small"
                              color={event.payload.mode === 'auto' ? 'success' : 'warning'}
                              variant="outlined"
                            />
                          )}
                          {event.payload.problem && (
                            <Tooltip title={event.payload.problem}>
                              <Chip label="Problem" size="small" variant="outlined" />
                            </Tooltip>
                          )}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </TimelineContent>
              </TimelineItem>
            );
          })}
        </Timeline>
      </Paper>
    </Box>
  );
}

export default EventHistoryTimeline;

