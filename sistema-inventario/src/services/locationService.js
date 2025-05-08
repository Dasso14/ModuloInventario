// inventory_api/app/services/locationsService.js
import { fetchApi } from './api'; // Assuming fetchApi is in './api.js' or similar

/**
 * Builds a query string from filter, pagination, and sorting objects.
 * @param {object} filters - Filter parameters (e.g., { name: 'Warehouse', is_active: true, parent_id: 1 | null }).
 * @param {object} pagination - Pagination parameters (e.g., { page: 1, limit: 10 }).
 * @param {object} sorting - Sorting parameters (e.g., { name: 'asc', created_at: 'desc' }). Key is field, value is 'asc' or 'desc'.
 * @returns {string} The query string, starting with '?' if parameters exist.
 */
const buildQueryString = (filters = {}, pagination = {}, sorting = {}) => {
  const params = new URLSearchParams();

  // Add filters
  for (const key in filters) {
    if (filters.hasOwnProperty(key) && filters[key] !== undefined) {
      if (key === 'is_active') {
         params.append(key, filters[key] ? 'true' : 'false');
      } else if (key === 'parent_id') {
         // Handle the 'null' case for parent_id explicitly
         if (filters[key] === null) {
            params.append(key, 'null');
         } else {
            params.append(key, filters[key]);
         }
      }
      else {
        params.append(key, filters[key]);
      }
    }
  }

  // Add pagination
  if (pagination.page !== undefined && pagination.limit !== undefined) {
    params.append('page', pagination.page);
    params.append('limit', pagination.limit);
  }
  // Add sorting (example: sort=name:asc,created_at:desc) - needs backend to parse this format
  const sortParams = Object.entries(sorting)
    .map(([field, order]) => `${field}:${order}`)
    .join(',');
  if (sortParams) {
    params.append('sort', sortParams);
  }


  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
};


// List all locations with optional filters, pagination, and sorting
export const getAllLocations = async (filters, pagination, sorting) => {
  const queryString = buildQueryString(filters, pagination, sorting);
  // Calls GET /api/locations?name=...&is_active=...&parent_id=...&page=...&limit=...&sort=...
  return fetchApi(`/locations/${queryString}`);
};

// Get a single location by ID
export const getLocationById = async (id) => {
  return fetchApi(`/locations/${id}`); // Calls GET /api/locations/:id
};

// Create a new location
export const createLocation = async (locationData) => {
  // locationData should match the expected payload for location creation
  // e.g., { name, description, parent_id, is_active }
  return fetchApi('/locations/', {
    method: 'POST',
    body: JSON.stringify(locationData),
  }); // Calls POST /api/locations
};

// Update an existing location
export const updateLocation = async (id, locationData) => {
  // locationData should contain the fields to update
  // Use PUT or PATCH depending on your API's convention (PATCH for partial updates is common)
  // The Python endpoint handles both, so either is fine, but PATCH is often preferred for updates.
  return fetchApi(`/locations/${id}`, {
    method: 'PATCH', // Or 'PUT'
    body: JSON.stringify(locationData),
  }); // Calls PATCH (or PUT) /api/locations/:id
};

// Delete a location (logical delete - sets is_active=False)
export const deleteLocation = async (id) => {
    // Note: Your Python DELETE endpoint performs a logical delete (setting is_active=False).
    // A true physical delete would typically return 204 No Content.
    // Since it returns a message, keeping it simple here.
    return fetchApi(`/locations/${id}`, {
        method: 'DELETE',
    }); // Calls DELETE /api/locations/:id
};

// Example of fetching root locations (parent_id = null)
export const getRootLocations = async (pagination, sorting) => {
    const filters = { parent_id: null };
    return getAllLocations(filters, pagination, sorting);
}

// You might add other specific functions if needed, e.g.,
// export const getChildrenLocations = async (parentId, pagination, sorting) => { ... }