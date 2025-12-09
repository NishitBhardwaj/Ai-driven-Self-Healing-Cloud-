import React, { useMemo, useState } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Box,
  Chip,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import { useTable } from 'react-table';
import { format } from 'date-fns';
import { Info, FilterList } from '@mui/icons-material';

/**
 * Log Table Component
 * Displays real-time logs with explanations and filtering
 */
function LogTable({ logs }) {
  const [agentFilter, setAgentFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  // Generate sample logs if not provided
  const sampleLogs = useMemo(() => {
    if (logs.length > 0) return logs;

    return Array.from({ length: 20 }, (_, i) => ({
      id: `log-${i}`,
      timestamp: new Date(Date.now() - i * 60000),
      agent_id: ['self-healing-001', 'scaling-001', 'security-001', 'monitoring-001'][i % 4],
      agent_name: ['Self-Healing Agent', 'Scaling Agent', 'Security Agent', 'Monitoring Agent'][i % 4],
      action: ['restart_pod', 'scale_up', 'block_ip', 'collect_metrics'][i % 4],
      explanation: [
        'Pod was restarted due to crash loop detection',
        'Scaled up from 3 to 5 replicas due to high CPU usage',
        'Blocked suspicious IP address after multiple failed login attempts',
        'Collected system metrics and updated health status',
      ][i % 4],
      confidence: 0.85 + Math.random() * 0.1,
      mode: i % 3 === 0 ? 'auto' : 'manual',
      type: ['info', 'success', 'warning', 'error'][i % 4],
    }));
  }, [logs]);

  const filteredLogs = useMemo(() => {
    return sampleLogs.filter((log) => {
      if (agentFilter !== 'all' && log.agent_id !== agentFilter) return false;
      if (typeFilter !== 'all' && log.type !== typeFilter) return false;
      return true;
    });
  }, [sampleLogs, agentFilter, typeFilter]);

  const uniqueAgents = useMemo(() => {
    const agents = [...new Set(sampleLogs.map((log) => log.agent_id))];
    return agents.map((id) => ({
      value: id,
      label: sampleLogs.find((log) => log.agent_id === id)?.agent_name || id,
    }));
  }, [sampleLogs]);

  const columns = useMemo(
    () => [
      {
        Header: 'Timestamp',
        accessor: 'timestamp',
        Cell: ({ value }) => format(new Date(value), 'yyyy-MM-dd HH:mm:ss'),
        width: 180,
      },
      {
        Header: 'Agent',
        accessor: 'agent_name',
        width: 200,
      },
      {
        Header: 'Action',
        accessor: 'action',
        Cell: ({ value }) => (
          <Chip label={value} size="small" color="primary" variant="outlined" />
        ),
        width: 150,
      },
      {
        Header: 'Explanation',
        accessor: 'explanation',
        Cell: ({ value, row }) => (
          <Tooltip title={value} arrow>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography
                variant="body2"
                sx={{
                  maxWidth: 400,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {value}
              </Typography>
              <IconButton size="small">
                <Info fontSize="small" />
              </IconButton>
            </Box>
          </Tooltip>
        ),
      },
      {
        Header: 'Confidence',
        accessor: 'confidence',
        Cell: ({ value }) => (
          <Chip
            label={`${(value * 100).toFixed(0)}%`}
            size="small"
            color={value >= 0.9 ? 'success' : value >= 0.7 ? 'warning' : 'error'}
          />
        ),
        width: 120,
      },
      {
        Header: 'Mode',
        accessor: 'mode',
        Cell: ({ value }) => (
          <Chip
            label={value === 'auto' ? 'Auto' : 'Manual'}
            size="small"
            color={value === 'auto' ? 'success' : 'warning'}
          />
        ),
        width: 100,
      },
      {
        Header: 'Type',
        accessor: 'type',
        Cell: ({ value }) => (
          <Chip
            label={value}
            size="small"
            color={
              value === 'error'
                ? 'error'
                : value === 'warning'
                ? 'warning'
                : value === 'success'
                ? 'success'
                : 'info'
            }
          />
        ),
        width: 100,
      },
    ],
    []
  );

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable({
    columns,
    data: filteredLogs,
  });

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">System Logs</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FilterList color="action" />
          <TextField
            select
            label="Filter by Agent"
            value={agentFilter}
            onChange={(e) => setAgentFilter(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="all">All Agents</MenuItem>
            {uniqueAgents.map((agent) => (
              <MenuItem key={agent.value} value={agent.value}>
                {agent.label}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Filter by Type"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            size="small"
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="info">Info</MenuItem>
            <MenuItem value="success">Success</MenuItem>
            <MenuItem value="warning">Warning</MenuItem>
            <MenuItem value="error">Error</MenuItem>
          </TextField>
        </Box>
      </Box>

      <TableContainer sx={{ maxHeight: 600 }}>
        <Table {...getTableProps()} stickyHeader>
          <TableHead>
            {headerGroups.map((headerGroup) => (
              <TableRow {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <TableCell
                    {...column.getHeaderProps()}
                    sx={{
                      backgroundColor: 'background.paper',
                      fontWeight: 'bold',
                      width: column.width,
                    }}
                  >
                    {column.render('Header')}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {rows.map((row) => {
              prepareRow(row);
              return (
                <TableRow {...row.getRowProps()} hover>
                  {row.cells.map((cell) => (
                    <TableCell {...cell.getCellProps()}>{cell.render('Cell')}</TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredLogs.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No logs found matching the selected filters
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

export default LogTable;

