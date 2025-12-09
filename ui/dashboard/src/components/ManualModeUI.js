import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Alert,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  ExpandMore,
  CheckCircle,
  Warning,
  Info,
  PlayArrow,
} from '@mui/icons-material';
import { format } from 'date-fns';

/**
 * Manual Mode UI Component
 * Shows error details and possible actions for user approval
 */
function ManualModeUI({ pendingDecisions, onConfirm }) {
  const [selectedOptions, setSelectedOptions] = useState({});

  const sampleDecisions = pendingDecisions.length > 0 ? pendingDecisions : [
    {
      id: 'decision-1',
      agent_id: 'scaling-001',
      agent_name: 'Scaling Agent',
      problem: 'CPU usage is at 95% and response times are increasing',
      reasoning: 'CPU usage has been above 90% for 5 minutes. The system needs more capacity to handle the current load.',
      options: [
        {
          id: 'scale_up',
          description: 'Scale up from 3 to 5 replicas',
          reasoning: 'Adding more replicas will distribute the load and reduce CPU usage per instance. This is a safe, low-risk action.',
          risk: 'low',
          impact: 'high',
          estimated_cost: 15.50,
        },
        {
          id: 'optimize',
          description: 'Optimize existing resources',
          reasoning: 'Optimize the current deployment configuration to better utilize existing resources. Lower cost but may not fully resolve the issue.',
          risk: 'medium',
          impact: 'medium',
          estimated_cost: 0.0,
        },
        {
          id: 'restart_service',
          description: 'Restart the service',
          reasoning: 'Restart the service to clear any memory leaks or stuck processes. Quick fix but may cause brief downtime.',
          risk: 'medium',
          impact: 'low',
          estimated_cost: 0.0,
        },
      ],
      confidence: 0.85,
      timestamp: new Date(),
    },
  ];

  const handleOptionSelect = (decisionId, optionId) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [decisionId]: optionId,
    }));
  };

  const handleConfirm = (decisionId) => {
    const optionId = selectedOptions[decisionId];
    if (optionId && onConfirm) {
      onConfirm(decisionId, optionId);
      setSelectedOptions((prev) => {
        const newState = { ...prev };
        delete newState[decisionId];
        return newState;
      });
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'low':
        return 'info';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  if (sampleDecisions.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No Pending Decisions
        </Typography>
        <Typography variant="body2" color="text.secondary">
          All decisions have been processed. The system is running smoothly.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {sampleDecisions.map((decision) => (
        <Card key={decision.id} elevation={3} sx={{ mb: 3 }}>
          <CardContent>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  {decision.agent_name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {format(new Date(decision.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                </Typography>
              </Box>
              <Chip
                label={`${(decision.confidence * 100).toFixed(0)}% Confidence`}
                color={decision.confidence >= 0.9 ? 'success' : 'warning'}
                size="small"
              />
            </Box>

            {/* Error/Problem Alert */}
            <Alert severity="warning" icon={<Warning />} sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Issue Detected
              </Typography>
              <Typography variant="body2">{decision.problem}</Typography>
            </Alert>

            {/* Reasoning */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography variant="subtitle2">Analysis & Reasoning</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  {decision.reasoning}
                </Typography>
              </AccordionDetails>
            </Accordion>

            {/* Available Actions */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2, mb: 1 }}>
              Available Actions
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Please review the options below and select an action:
            </Typography>

            <Grid container spacing={2}>
              {decision.options.map((option) => {
                const isSelected = selectedOptions[decision.id] === option.id;
                return (
                  <Grid item xs={12} md={6} key={option.id}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        border: isSelected ? 2 : 1,
                        borderColor: isSelected ? 'primary.main' : 'divider',
                        bgcolor: isSelected ? 'action.selected' : 'background.paper',
                        '&:hover': {
                          borderColor: 'primary.main',
                          bgcolor: 'action.hover',
                        },
                      }}
                      onClick={() => handleOptionSelect(decision.id, option.id)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {option.description}
                          </Typography>
                          {isSelected && <CheckCircle color="primary" />}
                        </Box>

                        <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                          <Chip
                            label={`Risk: ${option.risk}`}
                            color={getRiskColor(option.risk)}
                            size="small"
                          />
                          <Chip
                            label={`Impact: ${option.impact}`}
                            color={getImpactColor(option.impact)}
                            size="small"
                          />
                          {option.estimated_cost > 0 && (
                            <Chip
                              label={`Cost: $${option.estimated_cost.toFixed(2)}`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>

                        <Typography variant="body2" color="text.secondary">
                          {option.reasoning}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>

          <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrow />}
              disabled={!selectedOptions[decision.id]}
              onClick={() => handleConfirm(decision.id)}
              size="large"
            >
              Confirm Selection
            </Button>
          </CardActions>
        </Card>
      ))}
    </Box>
  );
}

export default ManualModeUI;

