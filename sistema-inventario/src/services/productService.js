// app/services/productService.js
import { fetchApi } from './api';

// List all products
export const getAllProducts = async () => {
  // Calls GET /api/products
  // Your Flask endpoint should handle optional filters, pagination, sorting
  return fetchApi('/products');
};

// Get a single product by ID
export const getProductById = async (id) => {
  // Calls GET /api/products/:id
  return fetchApi(`/products/${id}`);
};

// Create a new product
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
export const updateProduct = async (id, productData) => {
  // productData should contain the fields to update
  // Calls PUT /api/products/:id
  return fetchApi(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(productData),
  });
};

// Delete a product
export const deleteProduct = async (id) => {
    // Calls DELETE /api/products/:id
    return fetchApi(`/products/${id}`, {
        method: 'DELETE',
    });
};

// You might also need functions to get related data for forms, e.g., categories and suppliers
// These would likely call other services or dedicated endpoints if they return minimal data
// import { getAllCategories } from './categoryService';
// import { getAllSuppliers } from './supplierService';

// export const getProductFormData = async () => {
//   const categories = await getAllCategories();
//   const suppliers = await getAllSuppliers();
//   return { categories: categories.data, suppliers: suppliers.data };
// };
