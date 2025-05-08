// authService.js

// Import the generic fetchApi helper
import { fetchApi } from './api'; // Adjust the path as needed to point to your api.js file

/**
 * Calls the login endpoint to authenticate a user using fetchApi.
 * @param {string} identifier - The username or email.
 * @param {string} password - The user's password.
 * @returns {Promise<Object>} A promise that resolves with the login success data (e.g., user info).
 * @throws {Error} If authentication fails or an API error occurs (errors from fetchApi).
 */
const login = async (identifier, password) => {
  const url = '/auth/login'; // Endpoint path relative to API_BASE_URL
  const method = 'POST';
  const body = { identifier, password }; // Send body as an object, fetchApi will stringify

  try {
    // fetchApi already sets Content-Type: application/json and handles JSON body stringification
    const data = await fetchApi(url, {
      method: method,
      body: JSON.stringify(body), // fetchApi expects body to be stringified JSON if Content-Type is json
    });

    // fetchApi throws an error if response.ok is false
    // If we reach here, the HTTP status was 2xx and the JSON was parsed (or no content)

    // Although fetchApi handles !response.ok, your Flask endpoint might return
    // success: false with a 200 status for certain logical errors (less common but possible).
    // If your Flask backend *always* uses non-2xx for errors (like 401 for auth failure),
    // the check below is redundant after fetchApi handles it.
    // However, if your backend *might* return 200 with success: false, keep this:
    if (data && data.success === false) {
        const error = new Error(data.message || 'Login failed with success: false');
        error.data = data; // Attach full response data
        // You might add a status code here if data contains one, or derive it from the original response if you modified fetchApi to pass it
        throw error;
    }


    return data; // Return the successful data
  } catch (error) {
    console.error('Login API call failed:', error);
    // Re-throw the error so the caller can handle it (e.g., display error message)
    throw error;
  }
};

/**
 * Calls the register endpoint to create a new user using fetchApi.
 * @param {Object} userData - An object containing user registration data (e.g., { username, email, password }).
 * @returns {Promise<Object>} A promise that resolves with the registration success data (e.g., new user info).
 * @throws {Error} If registration fails or an API error occurs (errors from fetchApi).
 */
const register = async (userData) => {
  const url = '/auth/register'; // Endpoint path relative to API_BASE_URL
  const method = 'POST';
  const body = userData; // Send body as an object, fetchApi will stringify

  try {
     // fetchApi already sets Content-Type: application/json and handles JSON body stringification
    const data = await fetchApi(url, {
    
      method: method,
      body: JSON.stringify(body), // fetchApi expects body to be stringified JSON
    });

     // Similar check for success: false if your backend might return it with 2xx
     if (data && data.success === false) {
        const error = new Error(data.message || 'Registration failed with success: false');
        error.data = data;
        throw error;
     }

    return data; // Return the successful data
  } catch (error) {
    console.error('Registration API call failed:', error);
    // Re-throw the error
    throw error;
  }
};

// Export the functions
export { login, register };