import { useState, useCallback, useEffect } from 'react';
import { controlLED, controlBuzzer, getDeviceStatus } from '../services/api';

const useDeviceControl = (pubnubSendCommand = null, pubnubMessages = []) => {
  const [deviceStates, setDeviceStates] = useState({
    led: { state: 'unknown', brightness: 100 },
    buzzer: { state: 'unknown' },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch initial status
  useEffect(() => {
    const fetchInitialStatus = async () => {
      try {
        const status = await getDeviceStatus();
        if (status) {
          console.log('[useDeviceControl] 📊 Initial status:', status);
          setDeviceStates({
            led: status.led || { state: 'off', brightness: 100 },
            buzzer: status.buzzer || { state: 'off' },
          });
        }
      } catch (err) {
        console.error('[useDeviceControl] Failed to fetch initial status:', err);
      }
    };

    fetchInitialStatus();
  }, []);

  // Listen to PubNub updates
  useEffect(() => {
    if (! pubnubMessages || pubnubMessages.length === 0) return;

    const latestMessage = pubnubMessages[0];
    
    console.log('[useDeviceControl] 📨 Processing message:', {
      channel: latestMessage.channel,
      type: latestMessage.message?.type,
      device: latestMessage.message?.device,
      publisher: latestMessage.publisher,
    });
    
    const messageType = latestMessage?.message?.type;
    const device = latestMessage?.message?.device;
    
    if (messageType === 'state_update' && device) {
      const { state, parameters } = latestMessage.message;
      
      console.log(`[useDeviceControl] 🔔 State update from PubNub: ${device} = ${state}`);
      
      setDeviceStates(prev => ({
        ...prev,
        [device]: {
          ...prev[device],
          state,
          ...(parameters || {}),
        },
      }));
    }
  }, [pubnubMessages]);

  // Control LED
  const controlLed = useCallback(async (action, brightness = 100) => {
    setLoading(true);
    setError(null);

    try {
      console.log(`[useDeviceControl] 🎮 LED ${action} (brightness: ${brightness})`);
      
      // Send via API
      const result = await controlLED(action, brightness);
      
      console.log('[useDeviceControl] 📡 API response:', result);
      
      if (result.success && result.state) {
        const newState = {
          state: result.state,
          brightness: result.brightness || brightness,
        };
        
        console.log('[useDeviceControl] ✅ Updating from API:', newState);
        
        setDeviceStates(prev => ({
          ...prev,
          led: newState,
        }));
      }
      
      // Send via PubNub
      if (pubnubSendCommand) {
        await pubnubSendCommand('led', action, { brightness });
      }
      
      setTimeout(async () => {
        try {
          const status = await getDeviceStatus();
          if (status?.led) {
            console.log('[useDeviceControl] 🔄 Fallback sync from DB:', status.led);
            
            setDeviceStates(prev => {
              // Only update if different
              if (prev.led.state !== status.led.state || 
                  prev.led.brightness !== status.led.brightness) {
                console.log('[useDeviceControl] 📝 State changed, updating');
                return {
                  ...prev,
                  led: status.led,
                };
              }
              return prev;
            });
          }
        } catch (err) {
          console.error('[useDeviceControl] Fallback sync failed:', err);
        }
      }, 1000);

      setLoading(false);
      return result;
    } catch (err) {
      console.error('[useDeviceControl] ❌ LED control failed:', err);
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
      console.log(`[useDeviceControl] 🎮 Buzzer ${action}`);
      
      const result = await controlBuzzer(action);
      
      console.log('[useDeviceControl] 📡 API response:', result);
      
      // Update from API
      if (result.success && result.state) {
        console.log('[useDeviceControl] ✅ Updating from API:', result.state);
        
        setDeviceStates(prev => ({
          ...prev,
          buzzer: {
            state: result.state,
          },
        }));
      }
      
      // Send via PubNub
      if (pubnubSendCommand) {
        await pubnubSendCommand('buzzer', action);
      }
      
      // Fallback sync
      setTimeout(async () => {
        try {
          const status = await getDeviceStatus();
          if (status?.buzzer) {
            console.log('[useDeviceControl] 🔄 Fallback sync from DB:', status.buzzer);
            setDeviceStates(prev => ({
              ...prev,
              buzzer: status.buzzer,
            }));
          }
        } catch (err) {
          console.error('[useDeviceControl] Fallback sync failed:', err);
        }
      }, 1000);

      setLoading(false);
      return result;
    } catch (err) {
      console.error('[useDeviceControl] ❌ Buzzer control failed:', err);
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