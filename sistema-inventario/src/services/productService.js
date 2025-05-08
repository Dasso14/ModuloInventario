// app/services/productService.js
import { fetchApi } from './api'; // Asegúrate de que la ruta a tu fetchApi sea correcta

// List all products
// Acepta un queryString opcional para filtros, paginación y ordenación
export const getAllProducts = async (queryString = '') => {
  // Calls GET /api/products
  // Your Flask endpoint should handle optional filters, pagination, sorting
  return fetchApi(`/products/${queryString}`);
};

// Get a single product by ID
// Assumes the API returns { success: true, data: {...} } or { success: false, message: "..." }
export const getProductById = async (id) => {
  // Calls GET /api/products/:id
  return fetchApi(`/products/${id}`);
};

// Create a new product
// Assumes the API returns { success: true, data?: {...}, message?: string }
export const createProduct = async (productData) => {
  // productData should match the expected payload for product creation
  // e.g., { sku, name, description, category_id, supplier_id, ... }
  // Calls POST /api/products
  return fetchApi('/products', {
    method: 'POST',
    body: JSON.stringify(productData),
  });
};

// Update an existing product
// Assumes the API returns { success: true, data?: {...}, message?: string }
export const updateProduct = async (id, productData) => {
  // productData should contain the fields to update
  // Calls PUT /api/products/:id
  return fetchApi(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(productData),
  });
};

// Delete a product
// Assumes the API returns { success: true, message?: string }
export const deleteProduct = async (id) => {
    // Calls DELETE /api/products/:id
    return fetchApi(`/products/${id}`, {
        method: 'DELETE',
    });
};

// --- NEW FUNCTION TO GET STOCK LEVELS BY PRODUCT ID ---
// Assumes the API returns { success: true, data: [...] } or { success: false, message: "..." }
export const getProductStockLevels = async (productId) => {
    // Calls GET /api/products/{product_id}/stock-levels
    // This matches the new endpoint created in the Flask API
    return fetchApi(`/products/${productId}/stock-levels`);
};
// --- END NEW FUNCTION ---


// You might also need functions to get related data for forms, e.g., categories and suppliers
// These would likely call other services or dedicated endpoints if they return minimal data
// import { getAllCategories } from './categoryService';
// import { getAllSuppliers } from './supplierService';

// export const getProductFormData = async () => {
//   const categories = await getAllCategories();
//   const suppliers = await getAllSuppliers();
//   return { categories: categories.data, suppliers: suppliers.data };
// };
