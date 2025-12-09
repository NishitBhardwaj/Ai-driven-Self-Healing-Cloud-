import React from 'react';
import { Box, ToggleButton, ToggleButtonGroup, Typography, Tooltip } from '@mui/material';
import AutoModeIcon from '@mui/icons-material/FlashOn';
import ManualModeIcon from '@mui/icons-material/Person';

/**
 * Mode Toggle Component
 * Allows switching between Auto and Manual modes
 */
function ModeToggle({ mode, onModeChange }) {
  const handleModeChange = (event, newMode) => {
    if (newMode !== null) {
      onModeChange(newMode);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)' }}>
        System Mode
      </Typography>
      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={handleModeChange}
        aria-label="system mode"
        sx={{
          bgcolor: 'rgba(255,255,255,0.2)',
          '& .MuiToggleButton-root': {
            color: 'rgba(255,255,255,0.9)',
            borderColor: 'rgba(255,255,255,0.3)',
            '&.Mui-selected': {
              bgcolor: 'rgba(255,255,255,0.3)',
              color: 'white',
              '&:hover': {
                bgcolor: 'rgba(255,255,255,0.4)',
              },
            },
          },
        }}
      >
        <Tooltip title="Auto Mode - Agents act automatically">
          <ToggleButton value="auto" aria-label="auto mode">
            <AutoModeIcon sx={{ mr: 1 }} />
            Auto
          </ToggleButton>
        </Tooltip>
        <Tooltip title="Manual Mode - Requires user approval">
          <ToggleButton value="manual" aria-label="manual mode">
            <ManualModeIcon sx={{ mr: 1 }} />
            Manual
          </ToggleButton>
        </Tooltip>
      </ToggleButtonGroup>
    </Box>
  );
}

export default ModeToggle;

