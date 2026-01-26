import { VehicleInput, TcoResult } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'https://car-price-estimator-qva9.onrender.com';

export const checkHealth = async (): Promise<{ status: string; message?: string }> => {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      return { status: 'error', message: 'Backend returned an error' };
    }

    const data = await response.json();
    return { status: 'healthy', message: data.status };
  } catch (error) {
    return { status: 'error', message: 'Cannot connect to backend server' };
  }
};

export const estimateTco = async (vehicle: VehicleInput): Promise<TcoResult> => {
  const response = await fetch(`${API_URL}/api/tco/estimate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(vehicle),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to estimate TCO');
  }

  return response.json();
};
