// app/inventory/remove/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { getProducts, getLocations } from '../../../../lib/product-data'; // Datos para selects
import { useRouter } from 'next/navigation';

export default function RemoveInventoryPage() {
   const router = useRouter();
  const products = getProducts();
  const locations = getLocations();

  const [formData, setFormData] = useState({
    product_id: '',
    location_id: '',
    quantity: '',
    reference_number: '',
    notes: '',
    user_id: 1,
  });
    const [error, setError] = useState('');


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
     setError('');
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

    console.log('Registrando Salida:', formData);

     // --- Lógica para registrar la transacción (Salida) ---
    // fetch('/api/inventory/transactions', { ... })
    // Considerar validar stock disponible en el backend antes de registrar

    // Simulación:
    console.warn("¡Advertencia! En producción, validar stock disponible antes de permitir la salida.");
    alert(`Salida de ${formData.quantity} unidades del Producto ID ${formData.product_id} de Ubicación ID ${formData.location_id} registrada (simulado).`);
    router.push('/reports/transactions');

  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Registrar Salida de Inventario</h1>
             <Link href="/" passHref >
                 <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
            </Link>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <div className="card">
            <div className="card-body">
                <form onSubmit={handleSubmit}>
                    <div className="row g-3 mb-3">
                        <div className="col-md-6">
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
                            <label htmlFor="locationSelect" className="form-label">Ubicación de Origen</label>
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
                        <div className="form-text">
                           Ingrese la cantidad a remover.
                        </div>
                    </div>

                     <div className="mb-3">
                        <label htmlFor="referenceInput" className="form-label">Número de Referencia (Ej: Pedido de Venta)</label>
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

                    <button type="submit" className="btn btn-danger">
                        Registrar Salida
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}