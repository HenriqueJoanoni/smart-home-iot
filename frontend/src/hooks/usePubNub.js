/**
 * usePubNub Hook
 * Manages PubNub connection and real-time messages
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  initPubNub,
  subscribeToChannels,
  unsubscribeFromChannels,
  addMessageListener,
  removeListener,
  publishControlCommand,
} from '../services/pubnub';
import { CHANNELS } from '../utils/constants';

const usePubNub = (channels = [CHANNELS.SENSOR]) => {
  const [messages, setMessages] = useState([]);
  const [latestMessage, setLatestMessage] = useState(null);
  const [status, setStatus] = useState('disconnected');
  const [error, setError] = useState(null);
  
  const pubnubRef = useRef(null);
  const listenerRef = useRef(null);

  // Initialize PubNub
  useEffect(() => {
    console.log('[usePubNub] Initializing...');
    
    const pubnub = initPubNub();
    
    if (!pubnub) {
      console.error('[usePubNub] Failed to initialize');
      setStatus('error');
      setError('PubNub not configured. Check .env file.');
      return;
    }

    pubnubRef.current = pubnub;
    setStatus('connecting');

    // Add message listener
    const listener = addMessageListener(pubnub, (messageEvent) => {
      console.log('[usePubNub] Message received:', messageEvent);
      
      const newMessage = {
        channel: messageEvent.channel,
        message: messageEvent.message,
        timetoken: messageEvent.timetoken,
        timestamp: new Date(),
      };

      setLatestMessage(newMessage);
      setMessages(prev => [newMessage, ...prev.slice(0, 99)]);
      setStatus('connected');
    });

    listenerRef.current = listener;

    // Subscribe to channels
    const channelsArray = Array.isArray(channels) ? channels : [channels];
    subscribeToChannels(pubnub, channelsArray);

    console.log('[usePubNub] Subscribed to:', channelsArray);

    // Cleanup
    return () => {
      console.log('[usePubNub] Cleaning up...');
      
      if (pubnubRef.current) {
        if (listenerRef.current) {
          removeListener(pubnubRef.current, listenerRef.current);
        }
        unsubscribeFromChannels(pubnubRef.current, channelsArray);
        pubnubRef.current.stop();
      }
    };
  }, [channels]);

  // Publish control command
  const sendControlCommand = useCallback(async (device, action, params = {}) => {
    if (!pubnubRef.current) {
      console.error('[usePubNub] Not initialized');
      return false;
    }

    try {
      await publishControlCommand(pubnubRef.current, device, action, params);
      console.log(`[usePubNub] Control command sent: ${device} ${action}`);
      return true;
    } catch (err) {
      console.error('[usePubNub] Failed to send command:', err);
      return false;
    }
  }, []);

  // Get messages by channel
  const getMessagesByChannel = useCallback((channel) => {
    return messages.filter(msg => msg.channel === channel);
  }, [messages]);

  // Get latest sensor data from messages
  const getLatestSensorData = useCallback(() => {
    const sensorMessages = messages.filter(
      msg => msg.channel === CHANNELS.SENSOR && msg.message.type === 'sensor_data'
    );
    
    if (sensorMessages.length === 0) return null;
    
    return sensorMessages[0].message;
  }, [messages]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setLatestMessage(null);
  }, []);

  return {
    messages,
    latestMessage,
    status,
    error,
    sendControlCommand,
    getMessagesByChannel,
    getLatestSensorData,
    clearMessages,
    isConnected: status === 'connected',
  };
};

export default usePubNub;