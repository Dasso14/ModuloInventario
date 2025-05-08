// app/services/reportService.js
// Nota: Asegúrate de que './api' exporte una función fetchApi que maneje la URL base.
import { fetchApi } from './api';

// Eliminamos las funciones que construían query strings, ya que el backend no las usa.

/**
 * Fetches current stock levels.
 * (No longer supports filtering, pagination, or sorting parameters)
 * @returns {Promise<object>} - A promise that resolves with the API response.
 */
export const getStockLevels = async () => {
  // Llama a GET /api/reports/stock-levels sin parámetros de consulta
  return fetchApi('/reports/stock-levels');
};

/**
 * Fetches the low stock report.
 * (No longer supports filtering, pagination, or sorting parameters)
 * @returns {Promise<object>} - A promise that resolves with the API response.
 */
export const getLowStockReport = async () => {
  // Llama a GET /api/reports/low-stock sin parámetros de consulta
  return fetchApi('/reports/low-stock');
};

/**
 * Fetches the inventory transaction history.
 * (No longer supports filtering, pagination, or sorting parameters)
 * @returns {Promise<object>} - A promise that resolves with the API response.
 */
export const getTransactionHistory = async () => {
  // Llama a GET /api/reports/transactions sin parámetros de consulta
  return fetchApi('/reports/transactions');
};

/**
 * Fetches the stock transfer history.
 * (No longer supports filtering, pagination, or sorting parameters)
 * @returns {Promise<object>} - A promise that resolves with the API response.
 */
export const getTransferHistory = async () => {
  // Llama a GET /api/reports/transfers sin parámetros de consulta
  return fetchApi('/reports/transfers');
};

/**
 * Fetches the total inventory value.
 * (Does not take any parameters)
 * @returns {Promise<object>} - A promise that resolves with the API response containing the total value.
 */
export const getTotalInventoryValue = async () => {
  // Llama a GET /api/reports/total-value
  return fetchApi('/reports/total-value');
};