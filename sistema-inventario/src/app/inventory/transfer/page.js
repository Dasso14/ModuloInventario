// app/inventory/transfer/page.js
"use client";

import { useState, useEffect } from 'react'; // Import useEffect
import Link from 'next/link';
// Import services
import { getAllProducts } from '../../services/productService';
import { getAllLocations } from '../../services/locationService';
import { transferStock } from '../../services/inventoryService'; // Import transferStock
import { useRouter } from 'next/navigation';

export default function TransferInventoryPage() {
   const router = useRouter();
   const [products, setProducts] = useState([]);
   const [locations, setLocations] = useState([]);
   const [loading, setLoading] = useState(true); // Loading for dropdown data
   const [fetchError, setFetchError] = useState(null); // Error fetching dropdown data


  const [formData, setFormData] = useState({
    product_id: '',
    from_location_id: '',
    to_location_id: '',
    quantity: '',
    notes: '',
    // TODO: Replace hardcoded user_id with actual logged-in user's ID
    user_id: 1,
  });
    const [formError, setFormError] = useState(''); // Error for form submission
    const [isSubmitting, setIsSubmitting] = useState(false); // State for submission


   useEffect(() => {
      // Fetch products and locations concurrently
      const fetchData = async () => {
          setLoading(true);
          setFetchError(null);
          try {
              const [productsResponse, locationsResponse] = await Promise.all([
                  getAllProducts(),
                  getAllLocations()
              ]);

              if (productsResponse && productsResponse.success) {
                  setProducts(productsResponse.data);
              } else {
                  console.error('Failed to fetch products:', productsResponse?.message);
                  setFetchError('Error al cargar la lista de productos.');
              }

               if (locationsResponse && locationsResponse.success) {
                  setLocations(locationsResponse.data);
              } else {
                  console.error('Failed to fetch locations:', locationsResponse?.message);
                   setFetchError('Error al cargar la lista de ubicaciones.');
              }

          } catch (err) {
              console.error('Error fetching initial data:', err);
              setFetchError('Ocurrió un error al cargar los datos necesarios.');
          } finally {
              setLoading(false);
          }
      };

      fetchData();
  }, []); // Fetch data on component mount


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
     setFormError(''); // Clear error on change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    const quantityValue = parseFloat(formData.quantity);

    // --- Simple Validation ---
    if (!formData.product_id || !formData.from_location_id || !formData.to_location_id || isNaN(quantityValue) || quantityValue <= 0) {
         setFormError('Por favor, complete todos los campos requeridos con valores válidos.');
         return;
     }
     if (formData.from_location_id === formData.to_location_id) {
         setFormError('La ubicación de origen y destino deben ser diferentes.');
         return;
     }
     // --- End Simple Validation ---

    setIsSubmitting(true); // Disable button

    try {
        // Call the transferStock service function
        const response = await transferStock({
            ...formData,
            quantity: quantityValue, // Ensure quantity is sent as a number
             // Include user_id from state (replace hardcoded value later)
        });

        if (response && response.success) {
            console.log('Transferencia de stock registrada con éxito:', response.data);
             alert('Transferencia de stock registrada con éxito.');
            // Redirect to the transfers history report page
            router.push('/reports/transfers');
        } else {
             // Handle API-specific success: false response structure
             const errorMessage = response?.message || 'Error al registrar la transferencia de stock';
             setFormError(errorMessage);
             console.error('API Error registering stock transfer:', errorMessage);
              alert(`Error: ${errorMessage}`); // Show user-friendly error
        }

    } catch (err) {
        console.error('Error registering stock transfer:', err);
        setFormError(err.message || 'Ocurrió un error al registrar la transferencia.');
         alert(`Error: ${err.message || 'Ocurrió un error'}`); // Show user-friendly error
    } finally {
        setIsSubmitting(false); // Re-enable button
    }
  };

   // Show loading state for dropdown data
   if (loading) {
       return <div className="text-center text-primary">Cargando datos de productos y ubicaciones...</div>;
   }

    // Show error if fetching dropdown data failed
    if (fetchError) {
       return <div className="alert alert-danger">Error al cargar los datos: {fetchError}</div>;
    }


  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Transferir Stock entre Ubicaciones</h1>
             {/* Adjust the back link destination if needed */}
             <Link href="/inventory" passHref > {/* Assuming /inventory is an index page */}
                 <button type="button" className="btn btn-secondary">Volver</button>
            </Link>
        </div>

        {formError && <div className="alert alert-danger">{formError}</div>}

        <div className="card">
            <div className="card-body">
                <form onSubmit={handleSubmit}>
                     <div className="mb-3">
                        <label htmlFor="productSelect" className="form-label">Producto</label>
                        <select
                            className="form-select"
                            id="productSelect"
                            name="product_id"
                            value={formData.product_id}
                            onChange={handleChange}
                            required
                             disabled={isSubmitting} // Disable while submitting
                        >
                            <option value="">Seleccione un producto</option>
                            {products.map(product => (
                                <option key={product.product_id} value={product.product_id}>{product.sku} - {product.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="row g-3 mb-3">
                         <div className="col-md-6">
                            <label htmlFor="fromLocationSelect" className="form-label">Ubicación de Origen</label>
                            <select
                                className="form-select"
                                id="fromLocationSelect"
                                name="from_location_id"
                                value={formData.from_location_id}
                                onChange={handleChange}
                                required
                                 disabled={isSubmitting} // Disable while submitting
                            >
                                <option value="">Seleccione ubicación de origen</option>
                                {locations.map(location => (
                                    <option key={location.location_id} value={location.location_id}>{location.name}</option>
                                ))}
                            </select>
                        </div>

                         <div className="col-md-6">
                            <label htmlFor="toLocationSelect" className="form-label">Ubicación de Destino</label>
                            <select
                                className="form-select"
                                id="toLocationSelect"
                                name="to_location_id"
                                value={formData.to_location_id}
                                onChange={handleChange}
                                required
                                 disabled={isSubmitting} // Disable while submitting
                            >
                                <option value="">Seleccione ubicación de destino</option>
                                {/* You might want to filter the destination location so it cannot be the same as the source */}
                                {locations.map(location => (
                                    <option key={location.location_id} value={location.location_id}>{location.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>


                    <div className="mb-3">
                         <label htmlFor="quantityInput" className="form-label">Cantidad a Transferir</label>
                        <input
                            type="number"
                            step="0.01"
                            className="form-control"
                             id="quantityInput"
                            name="quantity"
                            value={formData.quantity}
                            onChange={handleChange}
                            required
                            min="0.01"
                            disabled={isSubmitting} // Disable while submitting
                        />
                    </div>

                    <div className="mb-3">
                        <label htmlFor="notesTextarea" className="form-label">Notas (Opcional)</label>
                        <textarea
                            className="form-control"
                            id="notesTextarea"
                            rows="3"
                            name="notes"
                            value={formData.notes}
                            onChange={handleChange}
                             disabled={isSubmitting} // Disable while submitting
                        ></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                        {isSubmitting ? 'Confirmando...' : 'Confirmar Transferencia'}
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}
