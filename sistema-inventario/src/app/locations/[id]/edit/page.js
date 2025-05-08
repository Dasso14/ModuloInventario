// app/locations/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
// Adjust the import path based on where locationsService.js is relative to this file
// Assuming service is in app/services
import { getLocationById, getAllLocations, updateLocation } from '../../../../services/locationService';

export default function EditLocationPage() {
  const router = useRouter();
  const params = useParams();
  // Ensure locationId is a number, handle potential string from URL
  const locationId = params.id ? parseInt(params.id, 10) : null;

  const [location, setLocation] = useState(undefined); // Stores the original location data
  const [loading, setLoading] = useState(true); // Loading state for initial data fetch
  const [error, setError] = useState(null); // Error state for initial data fetch
  const [availableParents, setAvailableParents] = useState([]); // List of locations for parent select
  const [loadingParents, setLoadingParents] = useState(true); // Loading state for parents dropdown

  // State for the form data
  const [formData, setFormData] = useState({
    name: '',
    // Changed from address to description
    description: '',
    parent_location: '', // Use string empty for the select value (will store parent ID or empty string)
    storage_capacity: '',
    is_active: true,
  });
   const [formError, setFormError] = useState(''); // Error state for form submission
   const [submitting, setSubmitting] = useState(false); // State to prevent double submission


  useEffect(() => {
    // Check if locationId is a valid number before fetching
    if (locationId !== null && !isNaN(locationId)) {
      const fetchData = async () => {
        setLoading(true);
        setError(null); // Clear previous errors

        try {
          // Fetch the location data to edit
          const locationResponse = await getLocationById(locationId);

          if (locationResponse.success) {
              const foundLocation = locationResponse.data;
              setLocation(foundLocation);
              // Pre-populate the form with fetched data
              setFormData({
                name: foundLocation.name,
                // Changed from address to description
                description: foundLocation.description || '',
                // Set parent_location state to the parent's ID as a string, or '' if no parent
                parent_location: foundLocation.parent_location ? foundLocation.parent_location.id.toString() : '',
                // Convert storage_capacity to string for input, handle null/undefined
                storage_capacity: foundLocation.storage_capacity !== undefined && foundLocation.storage_capacity !== null ? foundLocation.storage_capacity.toString() : '',
                is_active: foundLocation.is_active,
              });
          } else {
               setError(locationResponse.message || `Failed to fetch location with ID ${locationId}`);
               setLocation(undefined); // Clear location data on error
          }

          // Fetch available locations for the parent dropdown (excluding the current location)
          setLoadingParents(true); // Start loading for parents
          const parentsResponse = await getAllLocations(); // Fetch all locations

          if (parentsResponse.success) {
              // Filter out the current location itself from the parent options
              const filteredParents = parentsResponse.data.filter(loc => loc.id !== locationId);
              setAvailableParents(filteredParents);
          } else {
              console.error("Failed to fetch parent locations:", parentsResponse.message);
              // Optionally set an error specific to parent fetching, or just log
          }

        } catch (err) {
             console.error(`Error fetching data for location ${locationId}:`, err);
             setError(`An error occurred while fetching data for location ID ${locationId}.`);
             setLocation(undefined); // Clear location data on error
        } finally {
            setLoading(false); // Always set main loading to false
            setLoadingParents(false); // Always set parents loading to false
        }
      };

      fetchData();
    } else {
         // Handle cases where the ID in the URL is invalid
         setError("ID de ubicación inválido en la URL.");
         setLoading(false);
         setLocation(undefined); // Ensure location is undefined for invalid ID
    }
  }, [locationId]); // Effect depends on locationId changes


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
    setFormError(''); // Clear form error on input change
  };

  const handleSubmit = async (e) => { // Made function async
    e.preventDefault();

    if (submitting) return; // Prevent multiple submissions

    setFormError(''); // Clear previous form errors

     const capacityValue = formData.storage_capacity === '' ? null : parseFloat(formData.storage_capacity);
     const parentIdValue = formData.parent_location === '' ? null : parseInt(formData.parent_location, 10);


    // --- Simple Validation ---
    if (!formData.name || formData.name.trim() === '') {
        setFormError('El nombre de la ubicación es obligatorio.');
        return;
    }
     if (formData.storage_capacity !== '' && (isNaN(capacityValue) || capacityValue < 0)) {
         setFormError('La capacidad de almacenamiento debe ser un número positivo.');
         return;
     }
     // Check if the selected parent ID is the same as the current location ID
     if (parentIdValue !== null && parentIdValue === locationId) {
          setFormError('Una ubicación no puede ser padre de sí misma.');
          return;
     }
    // Add more validation if needed (e.g., description length)
    // --- End Simple Validation ---

    setSubmitting(true); // Disable button and inputs

    const dataToSend = {
       name: formData.name.trim(), // Trim whitespace
       // Changed from address to description
       description: formData.description,
       // API expects parent_id, not parent_location
       parent_id: parentIdValue,
       storage_capacity: capacityValue,
       is_active: formData.is_active,
    };

    console.log(`Datos a actualizar para ubicación ID ${locationId}:`, dataToSend);

    try {
       // Call the service function to update the location
       const response = await updateLocation(locationId, dataToSend);

       // Assuming response is { success: true, message: '...', data: {...} } or { success: false, message: '...' }
       if (response.success) {
           alert(`Ubicación ${response.data.name} actualizada exitosamente!`); // Use a more sophisticated notification
           router.push(`/locations/${locationId}`); // Redirect to the details page
       } else {
           // Handle API errors (e.g., validation errors, conflict)
           setFormError(response.message || 'Error al actualizar la ubicación.');
       }
    } catch (err) {
       console.error(`Error updating location ${locationId}:`, err);
       setFormError('Ocurrió un error al intentar actualizar la ubicación.'); // Generic error for unexpected issues
    } finally {
        setSubmitting(false); // Re-enable the submit button
    }
  };

    if (loading) {
        return <div className="text-center">Cargando datos de la ubicación...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

     if (!location) {
        return <div className="alert alert-warning text-center">Ubicación no disponible para editar.</div>;
    }


  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Editar Ubicación: {location.name}</h1>
            {/* Use location.id for the cancel link */}
            <Link href={`/locations/${location.id}`} passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {formError && <div className="alert alert-danger">{formError}</div>}
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
                                    {/* Mapear las ubicaciones disponibles. Ensure the current location is not an option */}
                                    {availableParents.map(parentLoc => (
                                        // Use parentLoc.id here
                                        <option key={parentLoc.id} value={parentLoc.id}>
                                            {parentLoc.name}
                                        </option>
                                    ))}
                                </select>
                             )}
                             <div className="form-text">
                               Seleccione una ubicación si esta es una sub-ubicación. No se puede seleccionar a sí misma.
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
                        {submitting ? 'Actualizando...' : 'Actualizar Ubicación'}
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}
