// app/locations/create/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getLocations } from '../../../../lib/product-data'; // Datos para el select padre

export default function CreateLocationPage() {
  const router = useRouter();
  const [availableParents, setAvailableParents] = useState([]); // Lista de ubicaciones para seleccionar como padre

  const [formData, setFormData] = useState({
    name: '',
    address: '',
    parent_location: '', // Usar string vacío para el select
    storage_capacity: '',
    description: '',
    is_active: true, // Por defecto activa
  });
    const [error, setError] = useState('');


  useEffect(() => {
      // Cargar ubicaciones disponibles para seleccionar como padre
      const locations = getLocations();
      setAvailableParents(locations);
      // En un sistema real: fetch('/api/locations').then(...)
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
     // Manejar checkbox
     if (type === 'checkbox') {
         setFormData(prevState => ({
            ...prevState,
            [name]: checked,
         }));
     } else {
        setFormData(prevState => ({
          ...prevState,
          [name]: value,
        }));
     }
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

     const capacityValue = parseFloat(formData.storage_capacity);

    // --- Validación simple ---
    if (!formData.name) {
        setError('El nombre de la ubicación es obligatorio.');
        return;
    }
     if (formData.storage_capacity !== '' && (isNaN(capacityValue) || capacityValue < 0)) {
         setError('La capacidad de almacenamiento debe ser un número positivo.');
         return;
     }
    // --- Fin Validación simple ---


    console.log('Datos a enviar para crear ubicación:', formData);
    // Lógica para enviar datos a tu API para crear la ubicación
    // fetch('/api/locations', {
    //    method: 'POST',
    //    headers: { 'Content-Type': 'application/json' },
    //    body: JSON.stringify({
    //      ...formData,
    //      parent_location: formData.parent_location === '' ? null : parseInt(formData.parent_location, 10), // Convertir a null si no se seleccionó padre
    //      storage_capacity: formData.storage_capacity === '' ? null : capacityValue // Convertir a null o número
    //    }),
    // })
    // .then(...)

    alert('Ubicación creada (simulado)'); // Simulación
    router.push('/locations'); // Redirigir a la lista
  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Crear Nueva Ubicación</h1>
            <Link href="/locations" passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="nameInput" className="form-label">Nombre de la Ubicación</label>
                        <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required maxLength="255" />
                    </div>

                     <div className="mb-3">
                        <label htmlFor="addressTextarea" className="form-label">Dirección</label>
                        <textarea className="form-control" id="addressTextarea" rows="3" name="address" value={formData.address} onChange={handleChange}></textarea>
                    </div>

                     <div className="row g-3 mb-3">
                         <div className="col-md-6">
                            <label htmlFor="parentSelect" className="form-label">Ubicación Padre (Opcional)</label>
                            <select
                                className="form-select"
                                id="parentSelect"
                                name="parent_location"
                                value={formData.parent_location}
                                onChange={handleChange}
                            >
                                <option value="">Sin Ubicación Padre</option>
                                {/* Mapear las ubicaciones disponibles */}
                                {availableParents.map(location => (
                                    <option key={location.location_id} value={location.location_id}>{location.name}</option>
                                ))}
                            </select>
                             <div className="form-text">
                               Seleccione una ubicación si esta es una sub-ubicación (ej: un pasillo dentro de un almacén).
                            </div>
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="capacityInput" className="form-label">Capacidad de Almacenamiento (Opcional)</label>
                            <input type="number" step="0.01" className="form-control" id="capacityInput" name="storage_capacity" value={formData.storage_capacity} onChange={handleChange} min="0" />
                             <div className="form-text">
                               Capacidad en unidades o medida relevante.
                            </div>
                        </div>
                     </div>


                    <div className="mb-3">
                        <div className="form-check">
                            <input
                                className="form-check-input"
                                type="checkbox"
                                id="isActiveCheck"
                                name="is_active"
                                checked={formData.is_active}
                                onChange={handleChange}
                            />
                            <label className="form-check-label" htmlFor="isActiveCheck">
                                Ubicación Activa
                            </label>
                        </div>
                    </div>


                    <button type="submit" className="btn btn-primary">
                        Guardar Ubicación
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}