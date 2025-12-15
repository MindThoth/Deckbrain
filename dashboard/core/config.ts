/**
 * Dashboard configuration
 */

export const config = {
  // Core API base URL
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  
  // Default device ID for testing
  defaultDeviceId: process.env.NEXT_PUBLIC_DEFAULT_DEVICE_ID || 'test-vessel-001',
} as const;

