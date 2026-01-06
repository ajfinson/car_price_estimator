import { VehicleInput, TcoResult } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
