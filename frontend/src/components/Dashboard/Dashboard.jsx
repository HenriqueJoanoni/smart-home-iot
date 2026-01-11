/**
 * Main Dashboard Component
 */

import React from 'react';
import useSensorData from '../../hooks/useSensorData';
import usePubNub from '../../hooks/usePubNub';
import useDeviceControl from '../../hooks/useDeviceControl';
import useAlerts from '../../hooks/useAlerts';
import { CHANNELS } from '../../utils/constants';

// Components
import Header from '../Layout/Header';
import Footer from '../Layout/Footer';
import Loading from '../Common/Loading';
import ErrorBoundary from '../Common/ErrorBoundary';

// Sensor Cards
import TemperatureCard from '../SensorCards/TemperatureCard';
import HumidityCard from '../SensorCards/HumidityCard';
import LightCard from '../SensorCards/LightCard';
import MotionCard from '../SensorCards/MotionCard';

// Charts
import TemperatureChart from '../Charts/TemperatureChart';
import HumidityChart from '../Charts/HumidityChart';
import LightChart from '../Charts/LightChart';

// Controls
import LedControl from '../Controls/LedControl';
import BuzzerControl from '../Controls/BuzzerControl';

// Alerts
import AlertList from '../Alerts/AlertList';

import './Dashboard.scss';

const Dashboard = () => {
  // Hooks
  const { 
    latestReadings, 
    loading:  sensorsLoading, 
    lastUpdate 
  } = useSensorData(true);

  const { 
    status: pubnubStatus, 
    isConnected, 
    sendControlCommand 
  } = usePubNub([CHANNELS.SENSOR, CHANNELS.ALERT]);

  const { 
    deviceStates,
    toggleLed,
    beep,
    alarm,
    loading: controlLoading 
  } = useDeviceControl(sendControlCommand);

  const { 
    unresolvedAlerts, 
    unresolvedCount,
    resolve:  resolveAlert,
    loading: alertsLoading 
  } = useAlerts(true);

  // Initial loading
  if (sensorsLoading) {
    return <Loading fullscreen message="Loading Smart Home Dashboard..." />;
  }

  return (
    <ErrorBoundary>
      <div className="dashboard-layout">
        {/* Header */}
        <Header
          apiStatus={latestReadings ?  'online' : 'offline'}
          pubnubStatus={isConnected ? 'online' : 'connecting'}
          unresolvedAlerts={unresolvedCount}
        />

        {/* Main Content */}
        <main className="dashboard">
          <div className="dashboard__container">
            
            {/* Hero Section */}
            <section className="dashboard__hero">
              <h2 className="dashboard__title">Environmental Monitoring</h2>
              <p className="dashboard__description">
                Real-time monitoring of temperature, humidity, light, and motion sensors
              </p>
            </section>

            {/* Sensor Cards Grid */}
            <section className="dashboard__section">
              <h3 className="dashboard__section-title">Current Readings</h3>
              <div className="dashboard__grid dashboard__grid--cards">
                <TemperatureCard 
                  data={latestReadings?.temperature} 
                  loading={sensorsLoading} 
                />
                <HumidityCard 
                  data={latestReadings?.humidity} 
                  loading={sensorsLoading} 
                />
                <LightCard 
                  data={latestReadings?.light} 
                  loading={sensorsLoading} 
                />
                <MotionCard 
                  data={latestReadings?.motion} 
                  loading={sensorsLoading} 
                />
              </div>
            </section>

            {/* Charts Section */}
            <section className="dashboard__section">
              <h3 className="dashboard__section-title">Analytics (Last 24 Hours)</h3>
              <div className="dashboard__grid dashboard__grid--charts">
                <div className="dashboard__chart-card">
                  <h4 className="dashboard__chart-title">Temperature Trend</h4>
                  <TemperatureChart hours={24} limit={50} />
                </div>
                <div className="dashboard__chart-card">
                  <h4 className="dashboard__chart-title">Humidity Trend</h4>
                  <HumidityChart hours={24} limit={50} />
                </div>
                <div className="dashboard__chart-card">
                  <h4 className="dashboard__chart-title">Light Levels</h4>
                  <LightChart hours={24} limit={50} />
                </div>
              </div>
            </section>

            {/* Controls Section */}
            <section className="dashboard__section">
              <h3 className="dashboard__section-title">Device Controls</h3>
              <div className="dashboard__grid dashboard__grid--controls">
                <LedControl
                  onToggle={toggleLed}
                  loading={controlLoading}
                  currentState={deviceStates.led.state}
                  currentBrightness={deviceStates.led.brightness}
                />
                <BuzzerControl
                  onBeep={beep}
                  onAlarm={alarm}
                  loading={controlLoading}
                  currentState={deviceStates.buzzer.state}
                />
              </div>
            </section>

            {/* Alerts Section */}
            {unresolvedCount > 0 && (
              <section className="dashboard__section">
                <h3 className="dashboard__section-title">
                  Active Alerts ({unresolvedCount})
                </h3>
                <AlertList
                  alerts={unresolvedAlerts}
                  loading={alertsLoading}
                  onResolve={resolveAlert}
                  maxItems={5}
                />
              </section>
            )}

          </div>
        </main>

        {/* Footer */}
        <Footer lastUpdate={lastUpdate} />
      </div>
    </ErrorBoundary>
  );
};

export default Dashboard;