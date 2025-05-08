// app/locations/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getLocationById, getLocations } from '../../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function EditLocationPage() {
  const router = useRouter();
  const params = useParams();
  const locationId = params.id ? parseInt(params.id, 10) : null;

  const [location, setLocation] = useState(undefined); // Almacena los datos originales
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [availableParents, setAvailableParents] = useState([]); // Lista de ubicaciones para seleccionar como padre

  // Estado para el formulario
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    parent_location: '',
    storage_capacity: '',
    description: '',
    is_active: true,
  });
   const [formError, setFormError] = useState('');


  useEffect(() => {
    if (locationId !== null && !isNaN(locationId)) {
      setLoading(true);
      setError(null);

      // Cargar datos de la ubicación a editar
      const foundLocation = getLocationById(locationId);

      if (foundLocation) {
          setLocation(foundLocation);
          // Precargar el formulario
          setFormData({
            name: foundLocation.name,
            address: foundLocation.address || '',
            parent_location: foundLocation.parent_location ? foundLocation.parent_location.toString() : '', // string para select
            storage_capacity: foundLocation.storage_capacity !== undefined && foundLocation.storage_capacity !== null ? foundLocation.storage_capacity.toString() : '', // string para input
            description: foundLocation.description || '',
            is_active: foundLocation.is_active,
          });
           setLoading(false);
      } else {
           setError(`Ubicación con ID ${locationId} no encontrada.`);
           setLoading(false);
      }

      // Cargar ubicaciones disponibles para seleccionar como padre (excluir la ubicación actual)
      const locations = getLocations().filter(loc => loc.location_id !== locationId);
      setAvailableParents(locations);

      // En un sistema real:
      // fetch(`/api/locations/${locationId}`).then(...)
      // fetch('/api/locations').then(...).then(allLocs => setAvailableParents(allLocs.filter(...)))
    } else {
         setError("ID de ubicación inválido en la URL.");
         setLoading(false);
    }
  }, [locationId]);


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
    setFormError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError('');

     const capacityValue = parseFloat(formData.storage_capacity);

    // --- Validación simple ---
    if (!formData.name) {
        setFormError('El nombre de la ubicación es obligatorio.');
        return;
    }
     if (formData.storage_capacity !== '' && (isNaN(capacityValue) || capacityValue < 0)) {
         setFormError('La capacidad de almacenamiento debe ser un número positivo.');
         return;
     }
     if (formData.parent_location && parseInt(formData.parent_location, 10) === locationId) { // Doble check por si acaso
          setFormError('Una ubicación no puede ser padre de sí misma.');
          return;
     }
    // --- Fin Validación simple ---


    console.log(`Datos a actualizar para ubicación ID ${locationId}:`, formData);
    // Lógica para enviar los datos actualizados a tu API
    // fetch(`/api/locations/${locationId}`, {
    //    method: 'PUT',
    //    headers: { 'Content-Type': 'application/json' },
    //    body: JSON.stringify({
    //      ...formData,
    //      parent_location: formData.parent_location === '' ? null : parseInt(formData.parent_location, 10),
    //      storage_capacity: formData.storage_capacity === '' ? null : capacityValue
    //    }),
    // })
    // .then(...)


    alert(`Ubicación ${location?.name} actualizada (simulado)`); // Simulación
    router.push(`/locations/${locationId}`); // Redirigir a los detalles
  };

    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

     if (!location) {
        return <div className="alert alert-warning">Ubicación no disponible para editar.</div>;
    }


  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Editar Ubicación: {location.name}</h1>
            <Link href={`/locations/${location.location_id}`} passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {formError && <div className="alert alert-danger">{formError}</div>}
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
                                {/* Mapear las ubicaciones disponibles. Asegurarse de que la ubicación actual no aparezca como opción padre */}
                                {availableParents.map(parentLoc => (
                                    <option key={parentLoc.location_id} value={parentLoc.location_id}>
                                        {parentLoc.name}
                                    </option>
                                ))}
                            </select>
                             <div className="form-text">
                               Seleccione una ubicación si esta es una sub-ubicación. No se puede seleccionar a sí misma.
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
                        Actualizar Ubicación
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}