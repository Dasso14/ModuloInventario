// app/locations/page.js
"use client";

import { useState, useEffect, useCallback } from 'react'; // Import useCallback
import Link from 'next/link';
// Adjust the import path based on where locationsService.js is relative to this file
// Assuming service is in app/services
import { getAllLocations, deleteLocation } from '../../services/locationService';

export default function LocationListPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // Add error state

  // Function to fetch locations
  const fetchLocations = useCallback(async () => {
    setLoading(true);
    setError(null); // Clear previous errors
    try {
      // Call the service function - ignoring filters/pagination/sorting as requested for now
      // When backend supports them, pass {} or actual state variables here:
      // const response = await getAllLocations(filters, pagination, sorting);
      const response = await getAllLocations();

      // Assuming response is { success: true, data: [...] }
      if (response.success) {
        setLocations(response.data);
      } else {
        setError(response.message || 'Failed to fetch locations');
        setLocations([]); // Clear locations on error
      }
    } catch (err) {
      console.error("Error fetching locations:", err);
      setError('An error occurred while fetching locations.');
      setLocations([]); // Clear locations on error
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies, fetches on mount

  useEffect(() => {
    fetchLocations();
  }, [fetchLocations]); // Effect runs when fetchLocations changes (only on mount due to useCallback)

  const handleDelete = async (id) => { // Made function async
     if (confirm(`¿Está seguro de eliminar la ubicación con ID ${id}? (Logical Delete)`)) {
         try {
             setLoading(true); // Show loading indicator while deleting
             setError(null); // Clear previous errors

             const response = await deleteLocation(id);

             if (response.success) {
                 console.log(`Ubicación con ID: ${id} marcada como inactiva`);
                 // Refetch the list to show the updated state (is_active=False)
                 fetchLocations();
                 // Or update state locally:
                 // setLocations(prevLocations =>
                 //    prevLocations.map(loc =>
                 //       loc.location_id === id ? { ...loc, is_active: false } : loc
                 //    )
                 // );
             } else {
                 setError(response.message || `Failed to delete location ${id}`);
                 setLoading(false); // Hide loading if refetch didn't happen
             }
         } catch (err) {
             console.error(`Error deleting location ${id}:`, err);
             setError(`An error occurred while deleting location ${id}.`);
             setLoading(false); // Hide loading if refetch didn't happen
         }
     }
  };


  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  if (error) {
      return <div className="alert alert-danger text-center">{error}</div>;
  }

  if (locations.length === 0) {
       return (
           <>
               <div className="d-flex justify-content-between align-items-center mb-3">
                    <h1>Lista de Ubicaciones / Almacenes</h1>
                    <Link href="/locations/create" passHref >
                       <button type="button" className="btn btn-primary">Crear Nueva Ubicación</button>
                    </Link>
                </div>
                <div className="alert alert-info text-center">
                     No se encontraron ubicaciones.
                </div>
           </>
       );
  }


  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Lista de Ubicaciones / Almacenes</h1>
        <Link href="/locations/create" passHref >
           <button type="button" className="btn btn-primary">Crear Nueva Ubicación</button>
        </Link>
      </div>

       {/* Implementar vista de árbol si se desea mostrar jerarquía */}

      <div className="table-responsive">
        <table className="table table-striped table-bordered table-hover">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Ubicación Padre</th>
              <th>Capacidad</th>
              <th>Activa</th>
              {/* <th>Dirección</th> */}
              {/* <th>Descripción</th> */}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {locations.map(location => (
              // Assuming location object from API has properties like location_id, name, parent_location (object or null), storage_capacity, is_active
              <tr key={location.id}>
                <td>{location.id}</td>
                <td>{location.name}</td>
                <td>{location.parent_location?.name || 'N/A'}</td>
                 <td>{location.storage_capacity !== undefined && location.storage_capacity !== null ? location.storage_capacity : 'N/A'}</td>
                 <td>{location.is_active ? 'Sí' : 'No'}</td>
                <td>
                  <Link href={`/locations/${location.id}`} passHref >
                    <button type="button" className="btn btn-info btn-sm me-2">Ver</button>
                  </Link>
                   <Link href={`/locations/${location.id}/edit`} passHref >
                    <button type="button" className="btn btn-warning btn-sm me-2">Editar</button>
                  </Link>
                   {location.is_active && ( // Only show delete button if active? Or show 'Activate' for inactive?
                       <button
                           type="button"
                           className="btn btn-danger btn-sm"
                           onClick={() => handleDelete(location.id)}
                       >
                           Eliminar
                       </button>
                   )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}