// app/reports/transfers/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
// Import the service function to fetch transfer history data from the API
import { getTransferHistory } from '../../../services/reportService'; // Adjust the path as necessary

// Removed imports for simulated data:
// import { getLocationTransfers, getProductName, getLocationName, getUserName } from '../../../../lib/product-data';

import { useSearchParams } from 'next/navigation'; // To read URL parameters
// import { useRouter } from 'next/navigation'; // Uncomment if you implement filter form submission


export default function LocationTransfersReportPage() {
   const searchParams = useSearchParams();
   // const router = useRouter(); // Uncomment if you implement filter form submission

  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // State to handle API errors

   // State for filters, initialized from URL params or defaults
  const [filters, setFilters] = useState({
      productId: searchParams.get('productId') ? parseInt(searchParams.get('productId')) : null,
      fromLocationId: searchParams.get('fromLocationId') ? parseInt(searchParams.get('fromLocationId')) : null,
      toLocationId: searchParams.get('toLocationId') ? parseInt(searchParams.get('toLocationId')) : null,
      userId: searchParams.get('userId') ? parseInt(searchParams.get('userId')) : null,
      startDate: searchParams.get('startDate') || null, // YYYY-MM-DD string
      endDate: searchParams.get('endDate') || null, // YYYY-MM-DD string
      // Add other filter states as needed
  });

  // State for pagination
  const [pagination, setPagination] = useState({
      page: searchParams.get('page') ? parseInt(searchParams.get('page')) : 1,
      limit: searchParams.get('limit') ? parseInt(searchParams.get('limit')) : 20, // Default limit
  });

   // State for sorting
   const [sorting, setSorting] = useState({
       sortBy: searchParams.get('sortBy') || 'transfer_date', // Default sort by date
       order: searchParams.get('order') || 'desc', // Default order descending
   });


  useEffect(() => {
    const fetchTransferData = async () => {
      setLoading(true); // Start loading
      setError(null); // Clear previous errors

      try {
        // Prepare parameters for the API call (combine filters, pagination, sorting)
        const params = {
            ...filters,
            ...pagination,
            ...sorting,
        };

        // Call the service function to fetch transfer history from the API
        const response = await getTransferHistory(params);

        // Check if the API call was successful based on your response structure
        if (response && response.success) {
          // Update state with the fetched data
          setTransfers(response.data);
        } else {
          // Handle API error response
          setError(response?.message || 'Error al cargar el reporte de transferencias.');
          console.error('API Error fetching transfers:', response?.message);
        }
      } catch (err) {
        // Handle network or unexpected errors
        console.error('Error fetching transfer history report:', err);
        setError(err.message || 'Ocurrió un error inesperado al cargar el reporte.');
      } finally {
        setLoading(false); // End loading
      }
    };

    // Execute the fetch function
    fetchTransferData();

     // Dependency array: re-run effect when filters, pagination, or sorting change
    // Note: When implementing filter/pagination/sorting UI, update these states
    // which will trigger this effect.
  }, [filters, pagination, sorting]); // Dependencies


  // Show loading state
  if (loading) {
    return (
         <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
            <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Cargando...</span>
            </div>
            <div className="ms-2 text-primary">Cargando reporte de transferencias...</div>
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
        <h1>Reporte de Transferencias entre Ubicaciones</h1>
         {/* Adjust the back link destination if needed */}
         <Link href="/" passHref > {/* Assuming / is your dashboard */}
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       {/* Placeholder for Filters (Implement filter UI and state updates here) */}
        <div className="card mb-4"> {/* Increased bottom margin */}
            <div className="card-body">
                <h6 className="card-title">Filtros</h6>
                 {/* Example filter inputs - connect to state and update useEffect dependencies */}
                <form className="row g-3">
                   <div className="col-md-3">
                       <label htmlFor="filterProduct" className="form-label">Producto</label>
                        <select className="form-select form-select-sm" id="filterProduct"
                           // value={filters.productId || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, productId: e.target.value ? parseInt(e.target.value) : null})} // Update state
                       >
                           <option value="">Todos los productos</option>
                           {/* Map your products data here */}
                           {/* {products.map(prod => <option key={prod.id} value={prod.id}>{prod.sku} - {prod.name}</option>)} */}
                       </select>
                   </div>
                    <div className="col-md-3">
                       <label htmlFor="filterFromLocation" className="form-label">Origen</label>
                        <select className="form-select form-select-sm" id="filterFromLocation"
                           // value={filters.fromLocationId || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, fromLocationId: e.target.value ? parseInt(e.target.value) : null})} // Update state
                       >
                           <option value="">Todas las ubicaciones de origen</option>
                           {/* Map your locations data here */}
                           {/* {locations.map(loc => <option key={loc.id} value={loc.id}>{loc.name}</option>)} */}
                       </select>
                   </div>
                    <div className="col-md-3">
                       <label htmlFor="filterToLocation" className="form-label">Destino</label>
                        <select className="form-select form-select-sm" id="filterToLocation"
                           // value={filters.toLocationId || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, toLocationId: e.target.value ? parseInt(e.target.value) : null})} // Update state
                       >
                           <option value="">Todas las ubicaciones de destino</option>
                           {/* Map your locations data here */}
                           {/* {locations.map(loc => <option key={loc.id} value={loc.id}>{loc.name}</option>)} */}
                       </select>
                   </div>
                     <div className="col-md-2">
                       <label htmlFor="filterStartDate" className="form-label">Fecha Desde</label>
                       <input type="date" className="form-control form-control-sm" id="filterStartDate"
                           // value={filters.startDate || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, startDate: e.target.value || null})} // Update state
                       />
                   </div>
                    <div className="col-md-2">
                       <label htmlFor="filterEndDate" className="form-label">Fecha Hasta</label>
                       <input type="date" className="form-control form-control-sm" id="filterEndDate"
                           // value={filters.endDate || ''} // Connect to state
                           // onChange={(e) => setFilters({...filters, endDate: e.target.value || null})} // Update state
                       />
                   </div>
                    <div className="col-md-2 d-flex align-items-end"> {/* Align button to the bottom */}
                       {/* Filter button - onClick should trigger filter state update */}
                       <button type="button" className="btn btn-primary btn-sm w-100"
                           // onClick={() => { /* Trigger fetch by updating filter state */ }}
                           disabled // Disable until filter logic is implemented
                       >Aplicar Filtros</button>
                   </div>
               </form>
            </div>
        </div>


      {/* Display the report data */}
      {transfers.length === 0 ? (
           <div className="alert alert-info text-center" role="alert">
               No hay transferencias registradas con los filtros actuales.
           </div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      {/* Table headers - adjust based on actual data structure */}
                      <th>Fecha</th>
                      <th>Producto</th>
                      <th>Origen</th>
                      <th>Destino</th>
                      <th>Cantidad</th>
                      <th>Usuario</th>
                      <th>Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {/* Map over the fetched transfers */}
                    {transfers.map(transfer => (
                      // Use a unique key, like transfer_id
                      <tr key={transfer.transfer_id}>
                        {/* Access properties directly from the API response data */}
                        <td>{transfer.transfer_date ? new Date(transfer.transfer_date).toLocaleString() : 'N/A'}</td> {/* Format date */}
                        <td>{transfer.product_name}</td> {/* Assuming API returns product_name */}
                        <td>{transfer.from_location_name}</td> {/* Assuming API returns from_location_name */}
                        <td>{transfer.to_location_name}</td> {/* Assuming API returns to_location_name */}
                        <td>{transfer.quantity}</td>
                        <td>{transfer.user_username}</td> {/* Assuming API returns user_username */}
                        <td>{transfer.notes || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}
