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
        
                    {transfers.map(transfer => (
                      // Use a unique key, like transfer_id
                      <tr key={transfer.id}>
                        <td>{transfer.transfer_date ? new Date(transfer.transfer_date).toLocaleString() : 'N/A'}</td>
                        <td>{transfer.product_name}</td> 
                        <td>{transfer.from_location_name}</td> 
                        <td>{transfer.to_location_name}</td> 
                        <td>{transfer.quantity}</td>
                        <td>{transfer.user_username}</td>
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
