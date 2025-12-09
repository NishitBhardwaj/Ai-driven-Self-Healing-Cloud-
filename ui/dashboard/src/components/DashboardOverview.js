import React from 'react';
import { Grid, Paper, Typography, Box, Chip, LinearProgress } from '@mui/material';
import { TrendingUp, TrendingDown, CheckCircle, Error, Warning } from '@mui/icons-material';

/**
 * Dashboard Overview Component
 * Displays overall system health, agent statuses, and key metrics
 */
function DashboardOverview({ agents, systemHealth, systemMode }) {
  const getHealthColor = (health) => {
    if (health >= 0.9) return 'success';
    if (health >= 0.7) return 'warning';
    return 'error';
  };

  const getHealthLabel = (health) => {
    if (health >= 0.9) return 'Healthy';
    if (health >= 0.7) return 'Degraded';
    return 'Critical';
  };

  const activeAgents = agents.filter(a => a.status === 'running').length;
  const totalAgents = agents.length || 1;
  const agentHealth = activeAgents / totalAgents;

  const systemHealthValue = systemHealth?.overall_health || 0.95;
  const cpuUsage = systemHealth?.cpu_usage || 0;
  const memoryUsage = systemHealth?.memory_usage || 0;
  const errorRate = systemHealth?.error_rate || 0;

  return (
    <Grid container spacing={3}>
      {/* System Health Card */}
      <Grid item xs={12} md={4}>
        <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            System Health
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{ flexGrow: 1 }}>
              <LinearProgress
                variant="determinate"
                value={systemHealthValue * 100}
                color={getHealthColor(systemHealthValue)}
                sx={{ height: 10, borderRadius: 5, mb: 1 }}
              />
              <Typography variant="h4" color={getHealthColor(systemHealthValue) + '.main'}>
                {(systemHealthValue * 100).toFixed(0)}%
              </Typography>
            </Box>
            <Chip
              label={getHealthLabel(systemHealthValue)}
              color={getHealthColor(systemHealthValue)}
              sx={{ ml: 2 }}
            />
          </Box>
          <Typography variant="body2" color="text.secondary">
            Overall system health status
          </Typography>
        </Paper>
      </Grid>

      {/* Active Agents Card */}
      <Grid item xs={12} md={4}>
        <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Active Agents
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" color="primary.main">
              {activeAgents}/{totalAgents}
            </Typography>
            <Box sx={{ ml: 2, flexGrow: 1 }}>
              <LinearProgress
                variant="determinate"
                value={agentHealth * 100}
                color="primary"
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {activeAgents} of {totalAgents} agents running
          </Typography>
        </Paper>
      </Grid>

      {/* System Mode Card */}
      <Grid item xs={12} md={4}>
        <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            System Mode
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Chip
              label={systemMode === 'auto' ? 'Auto Mode' : 'Manual Mode'}
              color={systemMode === 'auto' ? 'success' : 'warning'}
              sx={{ fontSize: '1.2rem', height: 40, px: 2 }}
            />
          </Box>
          <Typography variant="body2" color="text.secondary">
            {systemMode === 'auto'
              ? 'Agents act automatically with explanations'
              : 'User approval required for actions'}
          </Typography>
        </Paper>
      </Grid>

      {/* Resource Usage Cards */}
      <Grid item xs={12} md={3}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            CPU Usage
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5">{cpuUsage.toFixed(1)}%</Typography>
            {cpuUsage > 80 ? (
              <TrendingUp color="error" />
            ) : (
              <TrendingDown color="success" />
            )}
          </Box>
          <LinearProgress
            variant="determinate"
            value={cpuUsage}
            color={cpuUsage > 80 ? 'error' : 'primary'}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>

      <Grid item xs={12} md={3}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Memory Usage
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5">{memoryUsage.toFixed(1)}%</Typography>
            {memoryUsage > 80 ? (
              <TrendingUp color="error" />
            ) : (
              <TrendingDown color="success" />
            )}
          </Box>
          <LinearProgress
            variant="determinate"
            value={memoryUsage}
            color={memoryUsage > 80 ? 'error' : 'primary'}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>

      <Grid item xs={12} md={3}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Error Rate
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5">{errorRate.toFixed(2)}%</Typography>
            {errorRate > 5 ? (
              <Error color="error" />
            ) : (
              <CheckCircle color="success" />
            )}
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(errorRate * 10, 100)}
            color={errorRate > 5 ? 'error' : 'success'}
            sx={{ mt: 1 }}
          />
        </Paper>
      </Grid>

      <Grid item xs={12} md={3}>
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Latency
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h5">
              {systemHealth?.latency_ms?.toFixed(0) || 0}ms
            </Typography>
            {(systemHealth?.latency_ms || 0) > 200 ? (
              <Warning color="warning" />
            ) : (
              <CheckCircle color="success" />
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default DashboardOverview;

