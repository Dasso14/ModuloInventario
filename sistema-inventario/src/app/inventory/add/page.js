// app/inventory/add/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link'; // Usamos Link de next/link
import { getProducts, getLocations } from '../../../../lib/product-data'; // Datos para selects
import { useRouter } from 'next/navigation';

export default function AddInventoryPage() {
  const router = useRouter();
  const products = getProducts(); // Obtiene datos de productos
  const locations = getLocations(); // Obtiene datos de ubicaciones

  const [formData, setFormData] = useState({
    product_id: '',
    location_id: '',
    quantity: '',
    reference_number: '',
    notes: '',
    user_id: 1, // ID de usuario mock
  });
    const [error, setError] = useState('');


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
     setError(''); // Limpiar error al cambiar algo
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    const quantityValue = parseFloat(formData.quantity);

    // --- Validación simple ---
     if (!formData.product_id || !formData.location_id || isNaN(quantityValue) || quantityValue <= 0) {
         setError('Por favor, complete todos los campos requeridos con valores válidos.');
         return;
     }
     // --- Fin Validación simple ---

    console.log('Registrando Entrada:', formData);

    // --- Lógica para registrar la transacción (Entrada) ---
    // fetch('/api/inventory/transactions', { ... })

    // Simulación:
    alert(`Entrada de ${formData.quantity} unidades del Producto ID ${formData.product_id} en Ubicación ID ${formData.location_id} registrada (simulado).`);
    router.push('/reports/transactions'); // Redirigir a la lista de transacciones (simulado)

  };

  return (
     <> {/* Usamos Fragmento porque el layout ya provee el contenedor principal */}
        {/* Encabezado con título y botón, usando flexbox de Bootstrap */}
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Registrar Entrada de Inventario</h1>
             <Link href="/" passHref >
                 <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                 {error && <div className="alert alert-danger">{error}</div>}
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
                            maxLength="100"
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
                        ></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Registrar Entrada
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}