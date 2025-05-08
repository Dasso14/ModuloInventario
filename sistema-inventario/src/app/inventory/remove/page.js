// app/inventory/remove/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
// Import services
import { getAllProducts } from '../../../services/productService'; // Assuming these services exist
import { getAllLocations } from '../../../services/locationService'; // Assuming these services exist
import { removeStock } from '../../../services/inventoryService'; // Import the removeStock function
import { useRouter } from 'next/navigation';

export default function RemoveInventoryPage() {
   const router = useRouter();
   const [products, setProducts] = useState([]);
   const [locations, setLocations] = useState([]);
   const [loading, setLoading] = useState(true); // Loading state for initial data fetch
   const [fetchError, setFetchError] = useState(null); // Error state for initial data fetch


  const [formData, setFormData] = useState({
    product_id: '',
    location_id: '',
    quantity: '', // Quantity to remove (must be positive)
    reference_number: '', // Optional reference number
    notes: '', // Optional notes
    // TODO: Replace hardcoded user_id with actual logged-in user's ID
    user_id: 1, // Example hardcoded user ID
  });
    const [formError, setFormError] = useState(''); // Error message for form submission
    const [isSubmitting, setIsSubmitting] = useState(false); // State to track form submission status


   // Effect hook to fetch initial data (products and locations) on component mount
   useEffect(() => {
      const fetchData = async () => {
          setLoading(true); // Start loading
          setFetchError(null); // Clear previous fetch errors
          try {
              // Fetch products and locations concurrently using Promise.all
              const [productsResponse, locationsResponse] = await Promise.all([
                  getAllProducts(),
                  getAllLocations()
              ]);

              // Process products response
              if (productsResponse && productsResponse.success) {
                  setProducts(productsResponse.data);
              } else {
                  // Log error and set fetch error state
                  console.error('Failed to fetch products:', productsResponse?.message);
                  setFetchError('Error al cargar la lista de productos.');
              }

              // Process locations response
               if (locationsResponse && locationsResponse.success) {
                  setLocations(locationsResponse.data);
              } else {
                  // Log error and set fetch error state
                  console.error('Failed to fetch locations:', locationsResponse?.message);
                   setFetchError('Error al cargar la lista de ubicaciones.');
              }

          } catch (err) {
              // Catch any unexpected errors during fetch
              console.error('Error fetching initial data:', err);
              setFetchError('Ocurrió un error al cargar los datos necesarios.');
          } finally {
              setLoading(false); // End loading regardless of success or failure
          }
      };

      fetchData(); // Execute the fetch function
  }, []); // Empty dependency array means this effect runs only once on mount


  // Handle input changes and update form state
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
     setFormError(''); // Clear form error when user starts typing again
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default browser form submission
     setFormError(''); // Clear previous form errors

    const quantityValue = parseFloat(formData.quantity);

    // --- Client-side Validation ---
     // Check if required fields are filled and quantity is a valid positive number
     if (!formData.product_id || !formData.location_id || isNaN(quantityValue) || quantityValue <= 0) {
         setFormError('Por favor, complete los campos Producto, Ubicación de Origen y Cantidad con valores válidos (Cantidad > 0).');
         return; // Stop submission if validation fails
     }
     // --- End Client-side Validation ---

     setIsSubmitting(true); // Disable the submit button and show loading state

    try {
        // Call the removeStock service function with prepared data
        const response = await removeStock({
            ...formData, // Include other form data (product_id, location_id, user_id, notes)
            quantity: quantityValue, // Ensure quantity is sent as a number (positive)
            // reference_number and notes are optional and included if present in formData
        });

        // Check the response from the service/API
        if (response && response.success) {
            console.log('Salida de inventario registrada con éxito:', response.data);
             // Use a simple alert for success as in original code, could be replaced
             alert('Salida de inventario registrada con éxito.');
            // Redirect to the transaction history report page on success
            router.push('/reports/transactions');
        } else {
             // Handle API-specific success: false response structure
             // Display the error message from the API if available, otherwise a generic one
             const errorMessage = response?.message || 'Error al registrar la salida de inventario';
             setFormError(errorMessage); // Set form error state
             console.error('API Error registering stock removal:', errorMessage);
             // Removed alert for errors, using formError state instead
        }

    } catch (err) {
        // Catch any network errors or errors thrown by the service function
        console.error('Error registering stock removal:', err);
        // Set form error state with the error message
        setFormError(err.message || 'Ocurrió un error inesperado al registrar la salida.');
         // Removed alert for errors, using formError state instead
    } finally {
        setIsSubmitting(false); // Re-enable the submit button after submission attempt
    }
  };

   // --- Render Loading or Error state for initial data fetch ---
   if (loading) {
       return (
           <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
               <div className="spinner-border text-primary" role="status">
                   <span className="visually-hidden">Cargando...</span>
               </div>
               <div className="ms-2 text-primary">Cargando datos de productos y ubicaciones...</div>
           </div>
       );
   }

    if (fetchError) {
       return (
            <div className="alert alert-danger text-center" role="alert">
                <strong>Error:</strong> {fetchError}
            </div>
        );
    }
   // --- End Render Loading or Error state ---


  return (
     <> {/* Usamos Fragmento porque el layout ya provee el contenedor principal */}
        {/* Encabezado con título y botón Volver */}
        <div className="d-flex justify-content-between align-items-center mb-4"> {/* Increased bottom margin */}
            <h1>Registrar Salida de Inventario</h1>
             {/* Adjust the back link destination if needed */}
             <Link href="/" passHref > {/* Assuming /inventory is an index page */}
                 <button type="button" className="btn btn-secondary">Volver a Inventario</button> {/* More descriptive text */}
            </Link>
        </div>

        <div className="card shadow-sm"> {/* Added shadow */}
            <div className="card-body">
                 {/* Display form error message if present */}
                 {formError && (
                    <div className="alert alert-danger mb-3" role="alert"> {/* Added bottom margin */}
                        {formError}
                    </div>
                 )}

                <form onSubmit={handleSubmit}>
                    {/* row with g-3 for spacing between columns */}
                    <div className="row g-3 mb-3">
                        <div className="col-md-6"> {/* col-md-6 takes half width on medium+ screens */}
                            <label htmlFor="productSelect" className="form-label">Producto <span className="text-danger">*</span></label> {/* Added required indicator */}
                            <select
                                className="form-select"
                                id="productSelect"
                                name="product_id"
                                value={formData.product_id}
                                onChange={handleChange}
                                required // HTML5 required attribute
                                disabled={isSubmitting} // Disable while submitting
                            >
                                <option value="">-- Seleccione un producto --</option> {/* Improved placeholder */}
                                {products.map(product => (
                                    // Ensure product_id is the correct key from your API response
                                    <option key={product.id} value={product.id}>{product.sku} - {product.name}</option>
                                ))}
                            </select>
                        </div>

                         <div className="col-md-6">
                            <label htmlFor="locationSelect" className="form-label">Ubicación de Origen <span className="text-danger">*</span></label> {/* Added required indicator */}
                            <select
                                className="form-select"
                                id="locationSelect"
                                name="location_id"
                                value={formData.location_id}
                                onChange={handleChange}
                                required // HTML5 required attribute
                                disabled={isSubmitting} // Disable while submitting
                            >
                                <option value="">-- Seleccione una ubicación --</option> {/* Improved placeholder */}
                                {locations.map(location => (
                                     // Ensure location_id is the correct key from your API response
                                    <option key={location.id} value={location.id}>{location.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="mb-3">
                         <label htmlFor="quantityInput" className="form-label">Cantidad <span className="text-danger">*</span></label> {/* Added required indicator */}
                        <input
                            type="number"
                            step="0.01" // Allows decimal quantities
                            className="form-control"
                             id="quantityInput"
                            name="quantity"
                            value={formData.quantity}
                            onChange={handleChange}
                            required // HTML5 required attribute
                            min="0.01" // Minimum positive value for removal
                            disabled={isSubmitting} // Disable while submitting
                        />
                        <div className="form-text">
                           Ingrese la cantidad a remover (debe ser mayor a 0).
                        </div>
                    </div>

                     <div className="mb-3">
                        <label htmlFor="referenceInput" className="form-label">Número de Referencia (Opcional)</label> {/* Clarified optional */}
                        <input
                            type="text"
                            className="form-control"
                            id="referenceInput"
                            name="reference_number"
                            value={formData.reference_number}
                            onChange={handleChange}
                            maxLength="100" // Added max length
                            disabled={isSubmitting} // Disable while submitting
                        />
                         <div className="form-text">Número de referencia opcional (ej: número de pedido de venta).</div> {/* Added helper text */}
                    </div>

                    <div className="mb-4"> {/* Increased bottom margin */}
                        <label htmlFor="notesTextarea" className="form-label">Notas (Opcional)</label> {/* Clarified optional */}
                        <textarea
                            className="form-control"
                            id="notesTextarea"
                            rows="3"
                            name="notes"
                            value={formData.notes}
                            onChange={handleChange}
                            disabled={isSubmitting} // Disable while submitting
                        ></textarea>
                         <div className="form-text">Detalles adicionales sobre la salida de inventario.</div> {/* Added helper text */}
                    </div>

                    {/* Submit button */}
                    <button
                        type="submit"
                        className="btn btn-danger w-100" // Full width button, danger color for removal
                        disabled={isSubmitting} // Disable button while submitting
                    >
                        {isSubmitting ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Registrando...
                            </>
                        ) : (
                            'Registrar Salida'
                        )}
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}
