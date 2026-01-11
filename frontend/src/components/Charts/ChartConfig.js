/**
 * Chart Configuration
 * Shared config for Recharts
 */

import { CHART_CONFIG } from '../../utils/constants';

export const chartMargins = {
  top: 10,
  right: 10,
  left: 0,
  bottom: 0,
};

export const axisStyle = {
  fontSize: 12,
  fill: '#6b7280',
};

export const gridStyle = {
  stroke: '#e5e7eb',
  strokeDasharray: '3 3',
};

export const tooltipStyle = {
  contentStyle: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  },
  labelStyle: {
    color: '#374151',
    fontWeight: 600,
  },
};

export const temperatureConfig = {
  stroke:  CHART_CONFIG.colors.temperature,
  fill: CHART_CONFIG.colors.temperature,
  fillOpacity: 0.2,
};

export const humidityConfig = {
  stroke: CHART_CONFIG.colors.humidity,
  fill: CHART_CONFIG.colors.humidity,
  fillOpacity: 0.2,
};

export const lightConfig = {
  stroke: CHART_CONFIG.colors.light,
  fill: CHART_CONFIG.colors.light,
  fillOpacity: 0.2,
};

export const formatXAxis = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

export const formatTooltipLabel = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};