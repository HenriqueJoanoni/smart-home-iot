/**
 * PubNub Service
 * Real-time communication via PubNub
 */

import PubNub from 'pubnub';
import { PUBNUB_CONFIG, CHANNELS } from '../utils/constants';

/**
 * Initialize PubNub instance
 */
export const initPubNub = () => {
  if (!PUBNUB_CONFIG.publishKey || !PUBNUB_CONFIG.subscribeKey) {
    console.error('PubNub keys not configured! ');
    return null;
  }

  const pubnub = new PubNub({
    publishKey: PUBNUB_CONFIG.publishKey,
    subscribeKey: PUBNUB_CONFIG.subscribeKey,
    uuid:  PUBNUB_CONFIG.uuid,
    ssl: true,
  });

  console.log('[PubNub] Initialized:', PUBNUB_CONFIG.uuid);
  
  return pubnub;
};

/**
 * Subscribe to channels
 */
export const subscribeToChannels = (pubnub, channels) => {
  if (!pubnub) return;

  pubnub.subscribe({
    channels: Array.isArray(channels) ? channels : [channels],
  });

  console.log('[PubNub] Subscribed to:', channels);
};

/**
 * Unsubscribe from channels
 */
export const unsubscribeFromChannels = (pubnub, channels) => {
  if (!pubnub) return;

  pubnub.unsubscribe({
    channels: Array.isArray(channels) ? channels : [channels],
  });

  console.log('[PubNub] Unsubscribed from:', channels);
};

/**
 * Add message listener
 */
export const addMessageListener = (pubnub, callback) => {
  if (!pubnub) return null;

  const listener = {
    status: (statusEvent) => {
      console.log('[PubNub] Status:', statusEvent.category);
      
      if (statusEvent.category === 'PNConnectedCategory') {
        console.log('✅ [PubNub] Connected');
      } else if (statusEvent.category === 'PNNetworkDownCategory') {
        console.warn('⚠️ [PubNub] Network down');
      } else if (statusEvent.category === 'PNNetworkUpCategory') {
        console.log('✅ [PubNub] Network restored');
      }
    },
    message: (messageEvent) => {
      console.log('[PubNub] Message received:', messageEvent);
      
      if (callback) {
        callback(messageEvent);
      }
    },
    presence: (presenceEvent) => {
      console.log('[PubNub] Presence:', presenceEvent);
    },
  };

  pubnub.addListener(listener);
  
  return listener;
};

/**
 * Remove listener
 */
export const removeListener = (pubnub, listener) => {
  if (!pubnub || !listener) return;
  
  pubnub.removeListener(listener);
  console.log('[PubNub] Listener removed');
};

/**
 * Publish message
 */
export const publishMessage = async (pubnub, channel, message) => {
  if (!pubnub) {
    console.error('[PubNub] Not initialized');
    return null;
  }

  try {
    const result = await pubnub.publish({
      channel,
      message,
    });
    
    console.log('[PubNub] Published:', result);
    return result;
  } catch (error) {
    console.error('[PubNub] Publish error:', error);
    throw error;
  }
};

/**
 * Get message history
 */
export const getHistory = async (pubnub, channel, count = 25) => {
  if (!pubnub) return [];

  try {
    const result = await pubnub.history({
      channel,
      count,
    });
    
    return result.messages || [];
  } catch (error) {
    console.error('[PubNub] History error:', error);
    return [];
  }
};

/**
 * Subscribe to sensor channel
 */
export const subscribeToSensorChannel = (pubnub) => {
  subscribeToChannels(pubnub, CHANNELS.SENSOR);
};

/**
 * Subscribe to alert channel
 */
export const subscribeToAlertChannel = (pubnub) => {
  subscribeToChannels(pubnub, CHANNELS.ALERT);
};

/**
 * Publish control command
 */
export const publishControlCommand = async (pubnub, device, action, params = {}) => {
  const message = {
    type: 'control_command',
    device,
    action,
    ...params,
    timestamp: new Date().toISOString(),
  };

  return publishMessage(pubnub, CHANNELS.CONTROL, message);
};

export default {
  initPubNub,
  subscribeToChannels,
  unsubscribeFromChannels,
  addMessageListener,
  removeListener,
  publishMessage,
  getHistory,
  subscribeToSensorChannel,
  subscribeToAlertChannel,
  publishControlCommand,
};