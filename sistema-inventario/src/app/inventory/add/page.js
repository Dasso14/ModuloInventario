// app/inventory/add/page.js
"use client";

import { useState, useEffect } from 'react'; // Import useEffect
import Link from 'next/link';
// Import services
import { getAllProducts } from '../../services/productService';
import { getAllLocations } from '../../services/locationService';
import { addStock } from '../../services/inventoryService';
import { useRouter } from 'next/navigation';

export default function AddInventoryPage() {
  const router = useRouter();
  const [products, setProducts] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true); // Loading for dropdown data
  const [fetchError, setFetchError] = useState(null); // Error fetching dropdown data

  const [formData, setFormData] = useState({
    product_id: '',
    location_id: '',
    quantity: '',
    reference_number: '',
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
     setFormError(''); // Clear form error on change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    const quantityValue = parseFloat(formData.quantity);

    // --- Simple Validation ---
     if (!formData.product_id || !formData.location_id || isNaN(quantityValue) || quantityValue <= 0) {
         setFormError('Por favor, complete todos los campos requeridos con valores válidos.');
         return;
     }
     // --- End Simple Validation ---

     setIsSubmitting(true); // Disable button


    try {
        // Call the addStock service function
        const response = await addStock({
            ...formData,
            quantity: quantityValue, // Ensure quantity is sent as a number
            // Include user_id from state (replace hardcoded value later)
        });

        if (response && response.success) {
            console.log('Entrada de inventario registrada con éxito:', response.data);
             alert('Entrada de inventario registrada con éxito.');
            // Redirect to the transaction history report page
            router.push('/reports/transactions');
        } else {
             // Handle API-specific success: false response structure
             const errorMessage = response?.message || 'Error al registrar la entrada de inventario';
             setFormError(errorMessage);
             console.error('API Error registering stock addition:', errorMessage);
              alert(`Error: ${errorMessage}`); // Show user-friendly error
        }

    } catch (err) {
        console.error('Error registering stock addition:', err);
        setFormError(err.message || 'Ocurrió un error al registrar la entrada.');
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
     <> {/* Usamos Fragmento porque el layout ya provee el contenedor principal */}
        {/* Encabezado con título y botón, usando flexbox de Bootstrap */}
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Registrar Entrada de Inventario</h1>
             {/* Adjust the back link destination if needed */}
             <Link href="/inventory" passHref > {/* Assuming /inventory is an index page */}
                 <button type="button" className="btn btn-secondary">Volver</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                 {formError && <div className="alert alert-danger">{formError}</div>}
                <form onSubmit={handleSubmit}>
                    {/* row con g-3 para espaciado entre columnas */}
                    <div className="row g-3 mb-3">
                        <div className="col-md-6"> {/* col-md-6 ocupa la mitad del ancho en pantallas medianas+ */}
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

                        <div className="col-md-6">
                            <label htmlFor="locationSelect" className="form-label">Ubicación de Destino</label>
                            <select
                                className="form-select"
                                id="locationSelect"
                                name="location_id"
                                value={formData.location_id}
                                onChange={handleChange}
                                required
                                disabled={isSubmitting} // Disable while submitting
                            >
                                <option value="">Seleccione una ubicación</option>
                                {locations.map(location => (
                                    <option key={location.location_id} value={location.location_id}>{location.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="mb-3">
                         <label htmlFor="quantityInput" className="form-label">Cantidad</label>
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
                         <div className="form-text">Ingrese la cantidad a añadir al stock.</div>
                    </div>

                     <div className="mb-3">
                        <label htmlFor="referenceInput" className="form-label">Número de Referencia (Ej: Factura)</label>
                        <input
                            type="text"
                            className="form-control"
                            id="referenceInput"
                            name="reference_number"
                            value={formData.reference_number}
                            onChange={handleChange}
<<<<<<< Updated upstream
                            maxLength="100"
=======
                             disabled={isSubmitting} // Disable while submitting
>>>>>>> Stashed changes
                        />
                    </div>

                    <div className="mb-3">
                        <label htmlFor="notesTextarea" className="form-label">Notas</label>
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
                        {isSubmitting ? 'Registrando...' : 'Registrar Entrada'}
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}