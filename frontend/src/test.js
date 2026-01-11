import { getLatestSensorReadings, checkHealth } from './services/api';

// Test API
export const testAPI = async () => {
  console.log('🧪 Testing API...');
  
  try {
    // Test health
    const health = await checkHealth();
    console.log('✅ Health:', health);
    
    // Test sensors
    const sensors = await getLatestSensorReadings();
    console.log('✅ Latest sensors:', sensors);
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
};