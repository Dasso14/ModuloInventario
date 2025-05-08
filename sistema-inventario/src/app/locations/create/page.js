// app/locations/create/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
// Adjust the import path based on where locationsService.js is relative to this file
// Assuming service is in app/services
import { getAllLocations, createLocation } from '../../../services/locationService';

export default function CreateLocationPage() {
  const router = useRouter();
  const [availableParents, setAvailableParents] = useState([]); // Lista de ubicaciones para seleccionar como padre
  const [loadingParents, setLoadingParents] = useState(true); // Loading state for parents dropdown

  const [formData, setFormData] = useState({
    name: '',
    // Changed from address to description
    description: '',
    parent_location: '', // Use string empty for the select value
    storage_capacity: '',
    is_active: true, // Default active
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false); // State to prevent double submission


  useEffect(() => {
      // Load available locations for selecting as parent
      const fetchParents = async () => {
          setLoadingParents(true);
          try {
              // Fetch all locations to populate the parent dropdown
              // We only need ID and Name for the dropdown
              const response = await getAllLocations(); // Again, ignoring filters for simplicity here

              if (response.success) {
                  // Filter out the current location itself if this were an edit page
                  // For create, all existing locations are potential parents
                  setAvailableParents(response.data);
              } else {
                  console.error("Failed to fetch parent locations:", response.message);
                  // Optionally set an error specific to parent fetching
              }
          } catch (err) {
               console.error("Error fetching parent locations:", err);
               // Optionally set an error specific to parent fetching
          } finally {
              setLoadingParents(false);
          }
      };

      fetchParents();
  }, []); // Effect runs only on mount

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
     // Handle checkbox
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
    setError(''); // Clear error on input change
  };

  const handleSubmit = async (e) => { // Made function async
    e.preventDefault();

    if (submitting) return; // Prevent multiple submissions

    setError(''); // Clear previous errors

     const capacityValue = formData.storage_capacity === '' ? null : parseFloat(formData.storage_capacity);
     const parentIdValue = formData.parent_location === '' ? null : parseInt(formData.parent_location, 10);


    // --- Simple Validation ---
    if (!formData.name || formData.name.trim() === '') {
        setError('El nombre de la ubicación es obligatorio.');
        return;
    }
     if (formData.storage_capacity !== '' && (isNaN(capacityValue) || capacityValue < 0)) {
         setError('La capacidad de almacenamiento debe ser un número positivo.');
         return;
     }
    // Add more validation if needed (e.g., description length)
    // --- End Simple Validation ---

    setSubmitting(true);

    const dataToSend = {
       name: formData.name.trim(), // Trim whitespace
       // Changed from address to description
       description: formData.description,
       // API expects parent_id, not parent_location
       parent_id: parentIdValue,
       storage_capacity: capacityValue,
       is_active: formData.is_active,
    };

    console.log('Datos a enviar para crear ubicación:', dataToSend);

    try {
       const response = await createLocation(dataToSend);

       if (response.success) {
           alert('Ubicación creada exitosamente!'); // Use a more sophisticated notification in a real app
           router.push('/locations'); // Redirect to the list
       } else {
           // Handle API errors (e.g., validation errors, conflict)
           setError(response.message || 'Error al crear la ubicación.');
       }
    } catch (err) {
       console.error('Error creating location:', err);
       setError('Ocurrió un error al intentar crear la ubicación.'); // Generic error for unexpected issues
    } finally {
        setSubmitting(false); // Re-enable the submit button
    }
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
                        <input
                            type="text"
                            className="form-control"
                            id="nameInput"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                            maxLength="255"
                            disabled={submitting} // Disable input while submitting
                         />
                    </div>

                     <div className="mb-3">
                        {/* Changed label and name from address to description */}
                        <label htmlFor="descriptionTextarea" className="form-label">Descripción</label>
                        <textarea
                           className="form-control"
                           id="descriptionTextarea"
                           rows="3"
                           name="description" // Changed name
                           value={formData.description} // Changed value
                           onChange={handleChange}
                           disabled={submitting} // Disable input while submitting
                        ></textarea>
                    </div>

                     <div className="row g-3 mb-3">
                         <div className="col-md-6">
                            <label htmlFor="parentSelect" className="form-label">Ubicación Padre (Opcional)</label>
                             {loadingParents ? (
                                 <select className="form-select" disabled>
                                     <option>Cargando ubicaciones...</option>
                                 </select>
                             ) : (
                                <select
                                    className="form-select"
                                    id="parentSelect"
                                    name="parent_location" // Corresponds to state key
                                    value={formData.parent_location}
                                    onChange={handleChange}
                                    disabled={submitting} // Disable input while submitting
                                >
                                    <option value="">Sin Ubicación Padre</option>
                                    {/* Mapear las ubicaciones disponibles */}
                                    {availableParents.map(location => (
                                        // Assuming the API returns location objects with 'id' and 'name'
                                        <option key={location.id} value={location.id}>
                                           {location.name}
                                        </option>
                                    ))}
                                </select>
                             )}
                             <div className="form-text">
                               Seleccione una ubicación si esta es una sub-ubicación (ej: un pasillo dentro de un almacén).
                            </div>
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="capacityInput" className="form-label">Capacidad de Almacenamiento (Opcional)</label>
                            <input
                               type="number"
                               step="0.01"
                               className="form-control"
                               id="capacityInput"
                               name="storage_capacity"
                               value={formData.storage_capacity}
                               onChange={handleChange}
                               min="0"
                               disabled={submitting} // Disable input while submitting
                             />
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
                                disabled={submitting} // Disable input while submitting
                            />
                            <label className="form-check-label" htmlFor="isActiveCheck">
                                Ubicación Activa
                            </label>
                        </div>
                    </div>


                    <button type="submit" className="btn btn-primary" disabled={submitting}>
                        {submitting ? 'Guardando...' : 'Guardar Ubicación'}
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}
