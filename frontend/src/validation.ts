import { VehicleInput } from './types';

class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export const validateVehicleInput = (vehicle: VehicleInput): void => {
  // Validate make
  if (!vehicle.make || typeof vehicle.make !== 'string') {
    throw new ValidationError('Make is required and must be a string');
  }

  if (vehicle.make.trim().length === 0) {
    throw new ValidationError('Make cannot be empty');
  }

  if (vehicle.make.length > 50) {
    throw new ValidationError('Make is too long (max 50 characters)');
  }

  // Validate model
  if (!vehicle.model || typeof vehicle.model !== 'string') {
    throw new ValidationError('Model is required and must be a string');
  }

  if (vehicle.model.trim().length === 0) {
    throw new ValidationError('Model cannot be empty');
  }

  if (vehicle.model.length > 50) {
    throw new ValidationError('Model is too long (max 50 characters)');
  }

  // Validate year
  if (typeof vehicle.year !== 'number' || isNaN(vehicle.year) || !isFinite(vehicle.year)) {
    throw new ValidationError('Year must be a valid number');
  }

  const currentYear = new Date().getFullYear();
  const minYear = 1900;
  const maxYear = currentYear + 1; // Allow next year's models

  if (vehicle.year < minYear || vehicle.year > maxYear) {
    throw new ValidationError(`Year must be between ${minYear} and ${maxYear}`);
  }

  if (!Number.isInteger(vehicle.year)) {
    throw new ValidationError('Year must be a whole number');
  }
};
