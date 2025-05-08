// app/reports/transactions/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
// Import the service function to fetch transaction history data from the API
import { getTransactionHistory } from '../../../services/reportService'; // Adjust the path as necessary

// Removed imports for simulated data:
// import { getInventoryTransactions, getProductName, getLocationName, getUserName } from '../../../../lib/product-data';

import { useSearchParams } from 'next/navigation'; // To read URL parameters
// import { useRouter } from 'next/navigation'; // Uncomment if you implement filter form submission

export default function TransactionHistoryReportPage() {
  const searchParams = useSearchParams();
  // const router = useRouter(); // Uncomment if you implement filter form submission

  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // State to handle API errors

  // State for filters, initialized from URL params or defaults
  const [filters, setFilters] = useState({
      productId: searchParams.get('productId') ? parseInt(searchParams.get('productId')) : null,
      locationId: searchParams.get('locationId') ? parseInt(searchParams.get('locationId')) : null,
      userId: searchParams.get('userId') ? parseInt(searchParams.get('userId')) : null,
      transactionType: searchParams.get('transactionType') || null, // e.g., 'add', 'remove', 'adjust'
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
       sortBy: searchParams.get('sortBy') || 'transaction_date', // Default sort by date
       order: searchParams.get('order') || 'desc', // Default order descending
   });


  useEffect(() => {
    const fetchTransactionData = async () => {
      setLoading(true); // Start loading
      setError(null); // Clear previous errors

      try {
        // Prepare parameters for the API call (combine filters, pagination, sorting)
        const params = {
            ...filters,
            ...pagination,
            ...sorting,
        };

        // Call the service function to fetch transaction history from the API
        const response = await getTransactionHistory(params);

        // Check if the API call was successful based on your response structure
        if (response && response.success) {
          // Update state with the fetched data
          setTransactions(response.data);
        } else {
          // Handle API error response
          setError(response?.message || 'Error al cargar el historial de transacciones.');
          console.error('API Error fetching transactions:', response?.message);
        }
      } catch (err) {
        // Handle network or unexpected errors
        console.error('Error fetching transaction history report:', err);
        setError(err.message || 'Ocurrió un error inesperado al cargar el historial.');
      } finally {
        setLoading(false); // End loading
      }
    };

    // Execute the fetch function
    fetchTransactionData();

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
            <div className="ms-2 text-primary">Cargando historial de transacciones...</div>
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
        <h1>Historial de Transacciones de Inventario</h1>
         {/* Adjust the back link destination if needed */}
         <Link href="/" passHref > {/* Assuming / is your dashboard */}
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>



      {/* Display the report data */}
      {transactions.length === 0 ? (
           <div className="alert alert-info text-center" role="alert">
               No hay transacciones registradas con los filtros actuales.
           </div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      {/* Table headers - adjust based on actual data structure */}
                      <th>Fecha</th>
                      <th>Tipo</th>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad</th>
                      <th>Referencia</th>
                      <th>Usuario</th>
                      <th>Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(tx => (
                      // Use a unique key, like transaction_id
                      <tr key={tx.id}>
                        <td>{tx.transaction_date ? new Date(tx.transaction_date).toLocaleString() : 'N/A'}</td> 
                         <td>
                             <span className={`badge ${tx.transaction_type === 'add' ? 'bg-success' : tx.transaction_type === 'remove' ? 'bg-danger' : tx.transaction_type === 'adjust' ? 'bg-warning' : 'bg-secondary'}`}>
                                 {tx.transaction_type === 'add' ? 'Entrada' : tx.transaction_type === 'remove' ? 'Salida' : tx.transaction_type === 'adjust' ? 'Ajuste' : tx.transaction_type}
                            </span>
                        </td>
                        <td>{tx.product_name}</td> 
                        <td>{tx.location_name}</td> 
                        <td>{tx.quantity}</td>
                        <td>{tx.reference_number || 'N/A'}</td>
                        <td>{tx.user_username}</td> 
                        <td>{tx.notes || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}
