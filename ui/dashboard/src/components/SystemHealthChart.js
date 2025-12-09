import React, { useMemo } from 'react';
import { Paper, Typography, Box, Grid } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

/**
 * System Health Chart Component
 * Displays system health metrics using Chart.js
 */
function SystemHealthChart({ data }) {
  // Generate sample data if not provided
  const chartData = useMemo(() => {
    const labels = Array.from({ length: 20 }, (_, i) => {
      const date = new Date();
      date.setMinutes(date.getMinutes() - (19 - i) * 5);
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    });

    const generateData = (base, variance) => {
      return labels.map(() => base + (Math.random() - 0.5) * variance);
    };

    return {
      labels,
      datasets: [
        {
          label: 'CPU Usage (%)',
          data: generateData(data?.cpu_usage || 65, 15),
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Memory Usage (%)',
          data: generateData(data?.memory_usage || 70, 10),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Error Rate (%)',
          data: generateData(data?.error_rate || 2, 1),
          borderColor: 'rgb(245, 158, 11)',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          fill: true,
          tension: 0.4,
        },
      ],
    };
  }, [data]);

  const barData = useMemo(() => {
    return {
      labels: ['CPU', 'Memory', 'Network', 'Storage'],
      datasets: [
        {
          label: 'Current Usage (%)',
          data: [
            data?.cpu_usage || 65,
            data?.memory_usage || 70,
            data?.network_usage || 45,
            data?.storage_usage || 60,
          ],
          backgroundColor: [
            'rgba(239, 68, 68, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
          ],
          borderColor: [
            'rgb(239, 68, 68)',
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(245, 158, 11)',
          ],
          borderWidth: 2,
        },
      ],
    };
  }, [data]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'System Health Over Time (Last 100 minutes)',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function (value) {
            return value + '%';
          },
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Current Resource Usage',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function (value) {
            return value + '%';
          },
        },
      },
    },
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Line Chart */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3, height: 400 }}>
            <Box sx={{ height: '100%' }}>
              <Line data={chartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>

        {/* Bar Chart */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, height: 400 }}>
            <Box sx={{ height: '100%' }}>
              <Bar data={barData} options={barOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default SystemHealthChart;

