// app/inventory/adjust/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { getProducts, getLocations } from '../../../../lib/product-data'; // Datos para selects
import { useRouter } from 'next/navigation';

export default function AdjustInventoryPage() {
   const router = useRouter();
  const products = getProducts();
  const locations = getLocations();

  const [formData, setFormData] = useState({
    product_id: '',
    location_id: '',
    quantity: '', // Cantidad a ajustar (puede ser positiva o negativa)
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

    const adjustmentQuantity = parseFloat(formData.quantity);

    // --- Validación simple ---
    if (!formData.product_id || !formData.location_id || isNaN(adjustmentQuantity) || adjustmentQuantity === 0) {
         setError('Por favor, complete todos los campos requeridos con una cantidad de ajuste válida (positiva o negativa, pero no cero).');
         return;
     }
      if (!formData.notes.trim()) { // Notas son importantes para ajustes
          setError('Por favor, ingrese el motivo del ajuste en las notas.');
          return;
      }
     // --- Fin Validación simple ---

    console.log('Registrando Ajuste:', formData);

     // --- Lógica para registrar la transacción (Ajuste) ---
    // fetch('/api/inventory/transactions', { ... })

    // Simulación:
    alert(`Ajuste de ${adjustmentQuantity} unidades del Producto ID ${formData.product_id} en Ubicación ID ${formData.location_id} registrado (simulado).`);
    router.push('/reports/transactions');
  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Ajuste de Stock</h1>
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
                            <label htmlFor="locationSelect" className="form-label">Ubicación</label>
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
                         <label htmlFor="quantityInput" className="form-label">Cantidad a Ajustar (+ para aumentar, - para disminuir)</label>
                        <input
                            type="number"
                            step="0.01"
                            className="form-control"
                            id="quantityInput"
                            name="quantity"
                            value={formData.quantity}
                            onChange={handleChange}
                            required
                        />
                        <div className="form-text">
                           Ingrese la cantidad exacta para ajustar el stock (ej: 5 para añadir, -3 para remover). No el nuevo total.
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="notesTextarea" className="form-label">Motivo del Ajuste (Notas)</label>
                        <textarea
                            className="form-control"
                            id="notesTextarea"
                            rows="3"
                            name="notes"
                            value={formData.notes}
                            onChange={handleChange}
                            required
                        ></textarea>
                    </div>

                    <button type="submit" className="btn btn-warning">
                        Registrar Ajuste
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}