/**
 * useDeviceControl Hook
 * Controls devices (LED, Buzzer) via API and PubNub
 */

import { useState, useCallback } from 'react';
import { controlLED, controlBuzzer, getDeviceStatus } from '../services/api';

const useDeviceControl = (pubnubSendCommand = null) => {
  const [deviceStates, setDeviceStates] = useState({
    led: { state: 'unknown', brightness: 100 },
    buzzer: { state: 'unknown' },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Control LED
  const controlLed = useCallback(async (action, brightness = 100) => {
    setLoading(true);
    setError(null);

    try {
      // Send via API
      const result = await controlLED(action, brightness);
      
      // Also send via PubNub if available
      if (pubnubSendCommand) {
        await pubnubSendCommand('led', action, { brightness });
      }

      // Update local state
      setDeviceStates(prev => ({
        ...prev,
        led: {
          state: action === 'on' ? 'on' :  'off',
          brightness,
        },
      }));

      setLoading(false);
      console.log('[useDeviceControl] LED controlled:', action, brightness);
      return result;
    } catch (err) {
      console.error('[useDeviceControl] LED control failed:', err);
      setError(err.message || 'Failed to control LED');
      setLoading(false);
      return null;
    }
  }, [pubnubSendCommand]);

  // Control Buzzer
  const controlBuzzerDevice = useCallback(async (action) => {
    setLoading(true);
    setError(null);

    try {
      // Send via API
      const result = await controlBuzzer(action);
      
      // Also send via PubNub if available
      if (pubnubSendCommand) {
        await pubnubSendCommand('buzzer', action);
      }

      // Update local state
      setDeviceStates(prev => ({
        ...prev,
        buzzer: {
          state: action,
        },
      }));

      setLoading(false);
      console.log('[useDeviceControl] Buzzer controlled:', action);
      return result;
    } catch (err) {
      console.error('[useDeviceControl] Buzzer control failed:', err);
      setError(err.message || 'Failed to control buzzer');
      setLoading(false);
      return null;
    }
  }, [pubnubSendCommand]);

  // Fetch device status
  const fetchDeviceStatus = useCallback(async () => {
    try {
      const status = await getDeviceStatus();
      
      if (status) {
        setDeviceStates({
          led: status.led || { state: 'unknown', brightness: 100 },
          buzzer: status.buzzer || { state: 'unknown' },
        });
      }

      return status;
    } catch (err) {
      console.error('[useDeviceControl] Failed to fetch device status:', err);
      return null;
    }
  }, []);

  // LED shortcuts
  const turnLedOn = useCallback((brightness = 100) => controlLed('on', brightness), [controlLed]);
  const turnLedOff = useCallback(() => controlLed('off'), [controlLed]);
  const toggleLed = useCallback(() => controlLed('toggle'), [controlLed]);

  // Buzzer shortcuts
  const beep = useCallback(() => controlBuzzerDevice('beep'), [controlBuzzerDevice]);
  const alarm = useCallback(() => controlBuzzerDevice('alarm'), [controlBuzzerDevice]);
  const buzzerOn = useCallback(() => controlBuzzerDevice('on'), [controlBuzzerDevice]);
  const buzzerOff = useCallback(() => controlBuzzerDevice('off'), [controlBuzzerDevice]);

  return {
    deviceStates,
    loading,
    error,
    
    // LED controls
    controlLed,
    turnLedOn,
    turnLedOff,
    toggleLed,
    
    // Buzzer controls
    controlBuzzer: controlBuzzerDevice,
    beep,
    alarm,
    buzzerOn,
    buzzerOff,
    
    // Fetch status
    fetchDeviceStatus,
  };
};

export default useDeviceControl;