// app/services/locationService.js
import { fetchApi } from './api';

// List all locations
export const getAllLocations = async () => {
  // Calls GET /api/locations
  // Your Flask endpoint should handle optional filters, pagination, sorting
  return fetchApi('/locations');
};

// Get a single location by ID
export const getLocationById = async (id) => {
  // Calls GET /api/locations/:id
  return fetchApi(`/locations/${id}`);
};

// Create a new location
export const createLocation = async (locationData) => {
  // locationData should match the expected payload
  // e.g., { name, description, is_active, storage_capacity, parent_location }
  // Calls POST /api/locations
  return fetchApi('/locations', {
    method: 'POST',
    body: JSON.stringify(locationData),
  });
};

// Update an existing location
export const updateLocation = async (id, locationData) => {
  // locationData should contain the fields to update
  // Calls PUT /api/locations/:id
  return fetchApi(`/locations/${id}`, {
    method: 'PUT',
    body: JSON.stringify(locationData),
  });
};

// Delete a location
export const deleteLocation = async (id) => {
    // Calls DELETE /api/locations/:id
    return fetchApi(`/locations/${id}`, {
        method: 'DELETE',
    });
};

// Might need function to get parent locations for dropdown
// export const getParentLocationsForDropdown = async () => {
//     const locations = await getAllLocations();
//     // Filter out locations that cannot be parents (e.g., themselves in edit, or maybe certain types)
//     return locations.data;
// };
