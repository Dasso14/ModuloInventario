// app/services/supplierService.js
import { fetchApi } from './api'; // Asegúrate de que la ruta a tu fetchApi sea correcta

// Lista todos los proveedores
// Acepta un queryString opcional para filtros, paginación y ordenación
export const getAllSuppliers = async (queryString = '') => {
  // Llama a GET /api/suppliers con los parámetros de consulta
  // Asumimos que tu API devuelve una estructura como { success: true, data: [...], pagination: {...} } o { success: false, message: "..." }
  // Y fetchApi devuelve el cuerpo JSON parseado.
  return fetchApi(`/suppliers/${queryString}`);
};

// Obtiene un solo proveedor por ID
export const getSupplierById = async (id) => {
  // Llama a GET /api/suppliers/:id
  // Asumimos que tu API devuelve una estructura como { success: true, data: {...} } o { success: false, message: "..." }
  // Y fetchApi devuelve el cuerpo JSON parseado.
  return fetchApi(`/suppliers/${id}`);
};

// Crea un nuevo proveedor
export const createSupplier = async (supplierData) => {
  // supplierData debe coincidir con el payload esperado para la creación
  // e.g., { name, contact_name, phone, email, address, tax_id }
  // Llama a POST /api/suppliers
  // Asumimos que tu API devuelve una estructura como { success: true, data: {...} } o { success: false, message: "..." }
  return fetchApi('/suppliers/', {
    method: 'POST',
    body: JSON.stringify(supplierData),
  });
};

// Actualiza un proveedor existente
export const updateSupplier = async (id, supplierData) => {
  // supplierData debe contener los campos a actualizar
  // Llama a PUT /api/suppliers/:id
  // Asumimos que tu API devuelve una estructura como { success: true, data: {...} } o { success: false, message: "..." }
  return fetchApi(`/suppliers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(supplierData),
  });
};

// Elimina un proveedor
export const deleteSupplier = async (id) => {
    // Llama a DELETE /api/suppliers/:id
    // Asumimos que tu API devuelve una estructura como { success: true, message: "..." } o { success: false, message: "..." }
    return fetchApi(`/suppliers/${id}`, {
        method: 'DELETE',
    });
};

// Podrías añadir funciones adicionales si son necesarias, por ejemplo, para paginación, búsqueda, etc.