// app/services/categoryService.js
import { fetchApi } from './api';

// List all categories
export const getAllCategories = async () => {
  return fetchApi('/categories/'); // Calls GET /api/categories
};

// Get a single category by ID
export const getCategoryById = async (id) => {
  return fetchApi(`/categories/${id}`); // Calls GET /api/categories/:id
};

// Create a new category
export const createCategory = async (categoryData) => {
  // categoryData should match the expected payload for category creation
  // e.g., { name, description, parent_id }
  return fetchApi('/categories/', {
    method: 'POST',
    body: JSON.stringify(categoryData),
  }); // Calls POST /api/categories
};

// Update an existing category
export const updateCategory = async (id, categoryData) => {
  // categoryData should contain the fields to update
  return fetchApi(`/categories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(categoryData),
  }); // Calls PUT /api/categories/:id
};

// Delete a category (common, though not explicitly shown in your diagram as a page)
export const deleteCategory = async (id) => {
    return fetchApi(`/categories/${id}`, {
        method: 'DELETE',
    }); // Calls DELETE /api/categories/:id
};

// Might need function to get parent categories for dropdown
// export const getParentCategoriesForDropdown = async () => { ... }