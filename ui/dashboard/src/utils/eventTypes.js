/**
 * Event Types and Handlers
 * Defines all event types that can be received via WebSocket
 */

export const EVENT_TYPES = {
  // Agent Events
  AGENT_ACTION: 'agent_action',
  AGENT_UPDATE: 'agent_update',
  AGENT_STATUS_CHANGE: 'agent_status_change',
  
  // Decision Events
  DECISION_PENDING: 'decision_pending',
  DECISION_EXECUTED: 'decision_executed',
  DECISION_APPROVED: 'decision_approved',
  DECISION_REJECTED: 'decision_rejected',
  
  // System Events
  SYSTEM_HEALTH: 'system_health',
  METRICS_UPDATE: 'metrics_update',
  RESOURCE_USAGE: 'resource_usage',
  
  // Action Events
  HEALING_ACTION: 'healing_action',
  SCALING_ACTION: 'scaling_action',
  SECURITY_ACTION: 'security_action',
  CODE_ACTION: 'code_action',
  MONITORING: 'monitoring',
  
  // Error Events
  ERROR_DETECTED: 'error_detected',
  ERROR_RESOLVED: 'error_resolved',
  
  // Task Events
  TASK_CREATED: 'task_created',
  TASK_RESOLVED: 'task_resolved',
  TASK_FAILED: 'task_failed',
  
  // Problem Events
  PROBLEM_DETECTED: 'problem_detected',
  PROBLEM_RESOLVED: 'problem_resolved',
  
  // Security Events
  SECURITY_ALERT: 'security_alert',
  THREAT_DETECTED: 'threat_detected',
  
  // Log Events
  LOG_ENTRY: 'log_entry',
  
  // Connection Events
  CONNECTION: 'connection',
  DISCONNECTION: 'disconnection',
};

/**
 * Event severity levels
 */
export const EVENT_SEVERITY = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
};

/**
 * Get event severity based on event type
 */
export const getEventSeverity = (eventType, payload = {}) => {
  if (eventType === EVENT_TYPES.ERROR_DETECTED || eventType === EVENT_TYPES.TASK_FAILED) {
    return EVENT_SEVERITY.ERROR;
  }
  if (eventType === EVENT_TYPES.SECURITY_ALERT || eventType === EVENT_TYPES.PROBLEM_DETECTED) {
    return EVENT_SEVERITY.WARNING;
  }
  if (eventType === EVENT_TYPES.TASK_RESOLVED || eventType === EVENT_TYPES.HEALING_ACTION) {
    return EVENT_SEVERITY.SUCCESS;
  }
  return EVENT_SEVERITY.INFO;
};

/**
 * Get event priority (higher = more important)
 */
export const getEventPriority = (eventType) => {
  const priorities = {
    [EVENT_TYPES.ERROR_DETECTED]: 10,
    [EVENT_TYPES.SECURITY_ALERT]: 9,
    [EVENT_TYPES.THREAT_DETECTED]: 9,
    [EVENT_TYPES.PROBLEM_DETECTED]: 8,
    [EVENT_TYPES.DECISION_PENDING]: 7,
    [EVENT_TYPES.HEALING_ACTION]: 6,
    [EVENT_TYPES.SCALING_ACTION]: 5,
    [EVENT_TYPES.AGENT_ACTION]: 4,
    [EVENT_TYPES.TASK_CREATED]: 3,
    [EVENT_TYPES.METRICS_UPDATE]: 2,
    [EVENT_TYPES.LOG_ENTRY]: 1,
  };
  return priorities[eventType] || 0;
};

/**
 * Check if event requires user attention
 */
export const requiresUserAttention = (eventType, payload = {}) => {
  return (
    eventType === EVENT_TYPES.DECISION_PENDING ||
    eventType === EVENT_TYPES.ERROR_DETECTED ||
    eventType === EVENT_TYPES.SECURITY_ALERT ||
    eventType === EVENT_TYPES.PROBLEM_DETECTED ||
    (eventType === EVENT_TYPES.AGENT_ACTION && payload.mode === 'manual')
  );
};

/**
 * Format event for display
 */
export const formatEvent = (event) => {
  const { type, payload } = event;
  
  return {
    ...event,
    severity: getEventSeverity(type, payload),
    priority: getEventPriority(type),
    requiresAttention: requiresUserAttention(type, payload),
    formatted: {
      title: getEventTitle(type, payload),
      message: getEventMessage(type, payload),
      icon: getEventIcon(type),
    },
  };
};

/**
 * Get event title
 */
const getEventTitle = (type, payload) => {
  const titles = {
    [EVENT_TYPES.AGENT_ACTION]: `${payload.agent_name || 'Agent'} Action`,
    [EVENT_TYPES.HEALING_ACTION]: 'Healing Action',
    [EVENT_TYPES.SCALING_ACTION]: 'Scaling Action',
    [EVENT_TYPES.ERROR_DETECTED]: 'Error Detected',
    [EVENT_TYPES.DECISION_PENDING]: 'Decision Pending',
    [EVENT_TYPES.DECISION_EXECUTED]: 'Decision Executed',
    [EVENT_TYPES.TASK_CREATED]: 'Task Created',
    [EVENT_TYPES.TASK_RESOLVED]: 'Task Resolved',
    [EVENT_TYPES.PROBLEM_DETECTED]: 'Problem Detected',
    [EVENT_TYPES.SECURITY_ALERT]: 'Security Alert',
  };
  return titles[type] || type;
};

/**
 * Get event message
 */
const getEventMessage = (type, payload) => {
  return (
    payload.explanation ||
    payload.message ||
    payload.reasoning ||
    payload.problem ||
    payload.error ||
    'Event occurred'
  );
};

/**
 * Get event icon name
 */
const getEventIcon = (type) => {
  const icons = {
    [EVENT_TYPES.HEALING_ACTION]: 'healing',
    [EVENT_TYPES.SCALING_ACTION]: 'trending_up',
    [EVENT_TYPES.ERROR_DETECTED]: 'error',
    [EVENT_TYPES.SECURITY_ALERT]: 'security',
    [EVENT_TYPES.DECISION_PENDING]: 'pending',
    [EVENT_TYPES.TASK_RESOLVED]: 'check_circle',
  };
  return icons[type] || 'info';
};

export default {
  EVENT_TYPES,
  EVENT_SEVERITY,
  getEventSeverity,
  getEventPriority,
  requiresUserAttention,
  formatEvent,
};

