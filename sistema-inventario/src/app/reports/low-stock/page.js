// app/reports/low-stock/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
// Import the service function to fetch low stock data from the API
import { getLowStockReport } from '../../../services/reportService'; // Adjust the path as necessary

// Removed imports for simulated data:
// import { getProducts, getStockLevels, getProductName, getLocationName } from '../../../../lib/product-data';

export default function LowStockReportPage() {
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // State to handle API errors

  // State for filters (will be implemented later)
  const [filters, setFilters] = useState({
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
       sortBy: null, // Default sort by... (e.g., 'product_name')
       order: 'asc', // Default order
   });


  useEffect(() => {
    const fetchLowStockData = async () => {
      setLoading(true); // Start loading
      setError(null); // Clear previous errors

      try {
        // Prepare parameters for the API call (combine filters, pagination, sorting)
        const params = {
            ...filters,
            ...pagination,
            ...sorting,
        };

        // Call the service function to fetch low stock data from the API
        const response = await getLowStockReport(params);

        // Check if the API call was successful based on your response structure
        if (response && response.success) {
          // Update state with the fetched data
          setLowStockItems(response.data);
        } else {
          // Handle API error response
          setError(response?.message || 'Error al cargar el reporte de stock bajo.');
          console.error('API Error fetching low stock:', response?.message);
        }
      } catch (err) {
        // Handle network or unexpected errors
        console.error('Error fetching low stock report:', err);
        setError(err.message || 'Ocurrió un error inesperado al cargar el reporte.');
      } finally {
        setLoading(false); // End loading
      }
    };

    // Execute the fetch function
    fetchLowStockData();

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
            <div className="ms-2 text-primary">Cargando reporte de stock bajo...</div>
        </div>
    );
  }

  // Show error state
  if (error) {
      return (
           <div className="alert alert-danger text-center" role="alert">
               <strong>Error:</strong> {error}
           </div>
       );
  }


  return (
    <>
      {/* Header with title and back button */}
      <div className="d-flex justify-content-between align-items-center mb-4"> {/* Increased bottom margin */}
        <h1>Reporte de Productos con Stock Bajo</h1>
         {/* Adjust the back link destination if needed */}
         <Link href="/" passHref > {/* Assuming / is your dashboard */}
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       {/* Placeholder for Filters (Implement filter UI and state updates here) */}
       <div className="card mb-4"> {/* Increased bottom margin */}
           <div className="card-body">
               <h6 className="card-title">Filtros</h6>
               {/* Example filter input - connect to state and update useEffect dependencies */}
               <div className="row g-3">
                   <div className="col-md-4">
                       <label htmlFor="filterLocation" className="form-label">Ubicación</label>
                       <select className="form-select form-select-sm" id="filterLocation"
                           // value={filters.locationId || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, locationId: e.target.value ? parseInt(e.target.value) : null})} // Update state
                       >
                           <option value="">Todas las ubicaciones</option>
                           {/* Map your locations data here */}
                           {/* {locations.map(loc => <option key={loc.id} value={loc.id}>{loc.name}</option>)} */}
                       </select>
                   </div>
                    <div className="col-md-4">
                       <label htmlFor="filterCategory" className="form-label">Categoría</label>
                        <select className="form-select form-select-sm" id="filterCategory"
                           // value={filters.categoryId || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, categoryId: e.target.value ? parseInt(e.target.value) : null})} // Update state
                       >
                           <option value="">Todas las categorías</option>
                           {/* Map your categories data here */}
                           {/* {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)} */}
                       </select>
                   </div>
                    {/* Add other filters (Supplier, etc.) */}
                    <div className="col-md-2 d-flex align-items-end"> {/* Align button to the bottom */}
                       {/* Filter button - onClick should trigger filter state update */}
                       <button type="button" className="btn btn-primary btn-sm w-100"
                           // onClick={() => { /* Trigger fetch by updating filter state */ }}
                           disabled // Disable until filter logic is implemented
                       >Aplicar Filtros</button>
                   </div>
               </div>
           </div>
       </div>


      {/* Display the report data */}
      {lowStockItems.length === 0 ? (
           <div className="alert alert-success text-center" role="alert"> {/* Added role="alert" */}
               No hay productos con stock bajo. ¡Inventario saludable!
           </div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad Actual</th>
                      <th>Stock Mínimo</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Map over the fetched lowStockItems */}
                    {lowStockItems.map((item, index) => (
                      // Use a unique key, like a combination of product_id and location_id if no stock_id is reliable
                      // Assuming low_stock view provides product_id and location_id as a composite key
                      <tr key={`${item.product_id}-${item.location_id}`}>
                        {/* Access properties directly from the API response data */}
                        <td>{item.sku}</td>
                        <td>{item.product_name}</td>
                        <td>{item.location_name}</td>
                        <td>{item.quantity}</td>
                        <td>{item.min_stock}</td>
                         <td>
                             {/* Link to product details page */}
                             <Link href={`/products/${item.product_id}`} passHref >
                                 <button type="button" className="btn btn-info btn-sm">Ver Producto</button>
                             </Link>
                         </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}
