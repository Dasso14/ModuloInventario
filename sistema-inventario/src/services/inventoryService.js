// app/services/inventoryService.js
import { fetchApi } from './api';

// Function to register an inventory addition (add stock)
export const addStock = async (transactionData) => {
  // transactionData should include:
  // product_id (int): The ID of the product.
  // location_id (int): The ID of the location where stock is added.
  // quantity (number): The positive quantity being added.
  // user_id (int): The ID of the user performing the action.
  // reference_number (string, optional): A reference number (e.g., invoice number).
  // notes (string, optional): Any relevant notes for the transaction.

  // Calls POST /api/inventory/add
  return fetchApi('/inventory/add', {
    method: 'POST',
    body: JSON.stringify(transactionData),
  });
};

// Function to register an inventory removal (remove stock)
export const removeStock = async (transactionData) => {
  // transactionData should include:
  // product_id (int): The ID of the product.
  // location_id (int): The ID of the location from where stock is removed.
  // quantity (number): The positive quantity being removed.
  // user_id (int): The ID of the user performing the action.
  // reference_number (string, optional): A reference number (e.g., sales order).
  // notes (string, optional): Any relevant notes for the transaction.

  // Calls POST /api/inventory/remove
  return fetchApi('/inventory/remove', {
    method: 'POST',
    body: JSON.stringify(transactionData),
  });
};

// Function to register an inventory adjustment
export const adjustStock = async (transactionData) => {
  // transactionData should include:
  // product_id (int): The ID of the product.
  // location_id (int): The ID of the location where stock is adjusted.
  // quantity (number): The quantity to adjust. Can be positive (increase) or negative (decrease).
  // user_id (int): The ID of the user performing the action.
  // reference_number (string, optional): A reference number.
  // notes (string): Notes are typically required for adjustments to explain the reason.

  // Calls POST /api/inventory/adjust
  return fetchApi('/inventory/adjust', {
    method: 'POST',
    body: JSON.stringify(transactionData),
  });
};

// Function to register a stock transfer between locations
export const transferStock = async (transferData) => {
  // transferData should include:
  // product_id (int): The ID of the product being transferred.
  // from_location_id (int): The ID of the source location.
  // to_location_id (int): The ID of the destination location.
  // quantity (number): The positive quantity being transferred.
  // user_id (int): The ID of the user performing the action.
  // notes (string, optional): Any relevant notes for the transfer.

  // Calls POST /api/inventory/transfer
  return fetchApi('/inventory/transfer', {
    method: 'POST',
    body: JSON.stringify(transferData),
  });
};

// You might also add functions here to fetch inventory-related data,
// although some might be covered by reportService or dedicated inventory endpoints.
// Example: Get stock level for a specific product/location
// export const getStockLevel = async (productId, locationId) => {
//   return fetchApi(`/inventory/stock-level?product_id=${productId}&location_id=${locationId}`);
// };
