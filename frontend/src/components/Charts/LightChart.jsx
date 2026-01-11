/**
 * Light Chart Component
 */

import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import useSensorData from '../../hooks/useSensorData';
import Loading from '../Common/Loading';
import {
  chartMargins,
  axisStyle,
  gridStyle,
  tooltipStyle,
  lightConfig,
  formatXAxis,
  formatTooltipLabel,
} from './ChartConfig';
import './Charts.scss';

const LightChart = ({ hours = 24, limit = 50 }) => {
  const { fetchHistory } = useSensorData(false);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const history = await fetchHistory('light', hours, limit);
        
        if (history && history.readings) {
          const formatted = history.readings.map(reading => ({
            timestamp: reading.timestamp,
            value: parseFloat(reading.value),
            time: formatXAxis(reading.timestamp),
          })).reverse();
          
          setData(formatted);
        }
      } catch (err) {
        console.error('Error loading light history:', err);
        setError('Failed to load chart data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [fetchHistory, hours, limit]);

  if (loading) {
    return (
      <div className="chart-container">
        <Loading size="small" message="Loading chart..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container chart-container--error">
        <p>{error}</p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="chart-container chart-container--empty">
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data} margin={chartMargins}>
          <defs>
            <linearGradient id="lightGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={lightConfig.stroke} stopOpacity={0.8} />
              <stop offset="95%" stopColor={lightConfig.stroke} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid {...gridStyle} />
          <XAxis 
            dataKey="time" 
            {...axisStyle}
            interval="preserveStartEnd"
          />
          <YAxis 
            {...axisStyle}
            domain={['dataMin - 50', 'dataMax + 50']}
            tickFormatter={(value) => `${value} lux`}
          />
          <Tooltip 
            {...tooltipStyle}
            labelFormatter={formatTooltipLabel}
            formatter={(value) => [`${value.toFixed(0)} lux`, 'Light']}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={lightConfig.stroke}
            fill="url(#lightGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LightChart;