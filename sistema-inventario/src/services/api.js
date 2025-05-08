// app/services/api.js

// Use an environment variable for the API base URL
// It's best practice to store sensitive or environment-specific config here.
// Make sure to set NEXT_PUBLIC_API_BASE_URL in your .env.local file
// Example: NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5000/api
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:5000/api'; // Default fallback

// Helper function for consistent fetch calls
export const fetchApi = async (url, options = {}) => {
  const defaultHeaders = {
    'Content-Type': 'application/json',
    // Add other default headers here, e.g., Authorization token
    // You'll need logic to get the token, e.g., from localStorage or a context/state
    // const token = localStorage.getItem('authToken');
    // if (token) {
    //   defaultHeaders['Authorization'] = `Bearer ${token}`;
    // }
    ...options.headers, // Allow overriding default headers
  };

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options, // Include method, body, cache, etc. from options
    headers: defaultHeaders,
  });

  // Check for HTTP errors (status code outside 200-299)
  if (!response.ok) {
    let errorData = {};
    try {
      // Attempt to parse error details if the response is JSON
      errorData = await response.json();
    } catch (e) {
      // Fallback error message if response is not JSON or parsing fails
      errorData = { message: `HTTP error! Status: ${response.status}` };
    }
    // Throw an error with the message from the API or a default
    throw new Error(errorData.message || `HTTP error! Status: ${response.status}`);
  }

  // Handle successful responses that might not have a body (e.g., 204 No Content)
  if (response.status === 204) {
    return null; // No content to return
  }

  // Parse JSON response for success cases with content
  try {
    return await response.json();
  } catch (e) {
    // Handle cases where response is OK but not JSON (less common for APIs)
    console.warn('Response was OK but not JSON:', await response.text()); // Log the response text
    return null; // Or decide how to handle non-JSON success responses
  }
};