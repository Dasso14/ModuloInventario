// app/inventory/transfer/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { getProducts, getLocations } from '../../../../lib/product-data'; // Datos para selects
import { useRouter } from 'next/navigation';

export default function TransferInventoryPage() {
   const router = useRouter();
  const products = getProducts();
  const locations = getLocations();

  const [formData, setFormData] = useState({
    product_id: '',
    from_location_id: '',
    to_location_id: '',
    quantity: '',
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
    if (!formData.product_id || !formData.from_location_id || !formData.to_location_id || isNaN(quantityValue) || quantityValue <= 0) {
         setError('Por favor, complete todos los campos requeridos con valores válidos.');
         return;
     }
     if (formData.from_location_id === formData.to_location_id) {
         setError('La ubicación de origen y destino deben ser diferentes.');
         return;
     }
     // --- Fin Validación simple ---


    console.log('Iniciando Transferencia:', formData);

     // --- Lógica para iniciar la transferencia (llamada a API que ejecuta procedure) ---
    // fetch('/api/inventory/transfer', { ... })
    // Validar stock disponible en origen en el backend

    // Simulación:
    console.warn("¡Advertencia! En producción, validar stock disponible en el origen antes de permitir la transferencia.");
    alert(`Transferencia de ${formData.quantity} unidades del Producto ID ${formData.product_id} de Ubicación ${formData.from_location_id} a Ubicación ${formData.to_location_id} registrada (simulado).`);
    router.push('/reports/transfers');
  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Transferir Stock entre Ubicaciones</h1>
             <Link href="/" passHref >
                 <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
            </Link>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

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
                            >
                                <option value="">Seleccione ubicación de destino</option>
                                {/* Puedes filtrar la ubicación de destino para que no sea igual al origen si deseas */}
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
                        ></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Confirmar Transferencia
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}