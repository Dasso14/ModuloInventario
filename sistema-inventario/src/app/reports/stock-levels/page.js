// app/reports/stock-levels/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
// Import the service function to fetch stock levels data from the API
import { getStockLevels } from '../../../services/reportService'; // Adjust the path as necessary

// Removed imports for simulated data:
// import { getStockLevels, getProductName, getLocationName } from '../../../../lib/product-data';

export default function StockLevelsReportPage() {
  const [stockLevels, setStockLevels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // State to handle API errors

   // State for filters (will be implemented later)
  const [filters, setFilters] = useState({
      productId: null,
      locationId: null,
      categoryId: null,
      supplierId: null,
      // Add other filter states as needed
  });

  // State for pagination (will be implemented later)
  const [pagination, setPagination] = useState({
      page: 1,
      limit: 20, // Default limit
  });

   // State for sorting (will be implemented later)
   const [sorting, setSorting] = useState({
       sortBy: 'product_name', // Default sort by product name
       order: 'asc', // Default order
   });


  useEffect(() => {
    const fetchStockLevelsData = async () => {
      setLoading(true); // Start loading
      setError(null); // Clear previous errors

      try {
         // Prepare parameters for the API call (combine filters, pagination, sorting)
        const params = {
            ...filters,
            ...pagination,
            ...sorting,
        };

        // Call the service function to fetch stock levels data from the API
        const response = await getStockLevels(params);

        // Check if the API call was successful based on your response structure
        if (response && response.success) {
          // Update state with the fetched data
          setStockLevels(response.data);
        } else {
          // Handle API error response
          setError(response?.message || 'Error al cargar el reporte de niveles de stock.');
           console.error('API Error fetching stock levels:', response?.message);
        }
      } catch (err) {
        // Handle network or unexpected errors
        console.error('Error fetching stock levels report:', err);
        setError(err.message || 'Ocurrió un error inesperado al cargar el reporte.');
      } finally {
        setLoading(false); // End loading
      }
    };

    // Execute the fetch function
    fetchStockLevelsData();

    // Dependency array: re-run effect when filters, pagination, or sorting change
    // (Filtering/Pagination/Sorting logic to be added later)
  }, [filters, pagination, sorting]); // Dependencies


  // Show loading state
  if (loading) {
    return (
         <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
            <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Cargando...</span>
            </div>
            <div className="ms-2 text-primary">Cargando reporte de niveles de stock...</div>
        </div>
    );
  }

  // Show error state
   if (error) {
       return (
            <div className="alert alert-danger text-center" role="alert"> {/* Added role="alert" */}
                <strong>Error:</strong> {error}
            </div>
        );
    }


  return (
    <>
      {/* Header with title and back button */}
      <div className="d-flex justify-content-between align-items-center mb-4"> {/* Increased bottom margin */}
        <h1>Reporte de Niveles de Stock</h1>
         <Link href="/" passHref > {/* Assuming / is your dashboard */}
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       

      {stockLevels.length === 0 ? (
           <div className="alert alert-info text-center" role="alert"> {/* Added role="alert" */}
               No hay niveles de stock registrados.
           </div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad</th>
                      <th>Última Actualización</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stockLevels.map(item => (
                      // Use a unique key, like stock_id if available, or a combination
                      // Assuming stock_levels table has a stock_id or product_id+location_id is unique
                      <tr key={item.stock_id || `${item.product_id}-${item.location_id}`}>
                        <td>{item.product_name}</td> 
                        <td>{item.location_name}</td> 
                        <td>{item.quantity}</td>
                        <td>{item.last_updated ? new Date(item.last_updated).toLocaleString() : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}
