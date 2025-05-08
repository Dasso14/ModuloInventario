// app/locations/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
// Adjust the import path based on where locationsService.js is relative to this file
// Assuming service is in app/services
import { getLocationById } from '../../../services/locationService';

export default function LocationDetailPage() {
  const params = useParams();
  // Ensure locationId is a number, handle potential string from URL
  const locationId = params.id ? parseInt(params.id, 10) : null;

  const [location, setLocation] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if locationId is a valid number before fetching
    if (locationId !== null && !isNaN(locationId)) {
      const fetchLocation = async () => {
        setLoading(true);
        setError(null); // Clear previous errors
        try {
          // Call the service function to get location details
          const response = await getLocationById(locationId);

          // Assuming response is { success: true, data: {...} } or { success: false, message: '...' }
          if (response.success) {
              setLocation(response.data);
          } else {
              // Handle cases where the API returns an error (e.g., location not found)
              setError(response.message || `Failed to fetch location with ID ${locationId}`);
              setLocation(undefined); // Clear location data on error
          }
        } catch (err) {
            // Handle network errors or other exceptions during the fetch
            console.error(`Error fetching location ${locationId}:`, err);
            setError(`An error occurred while fetching location details for ID ${locationId}.`);
            setLocation(undefined); // Clear location data on error
        } finally {
           setLoading(false); // Always set loading to false after fetch attempt
        }
      };

      fetchLocation();
    } else {
         // Handle cases where the ID in the URL is invalid
         setError("ID de ubicación inválido en la URL.");
         setLoading(false);
         setLocation(undefined); // Ensure location is undefined for invalid ID
    }
  }, [locationId]); // Effect depends on locationId changes


    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    // Show a message if location is still undefined after loading (e.g., API returned success: false)
    if (!location) {
        return <div className="alert alert-warning text-center">Ubicación no disponible.</div>;
    }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles de la Ubicación: {location.name}</h1>
        <div>
           {/* Use location.id for the edit link */}
           <Link href={`/locations/${location.id}/edit`} passHref >
              <button type="button" className="btn btn-warning me-2">Editar</button>
            </Link>
            <Link href="/locations" passHref >
              <button type="button" className="btn btn-secondary">Volver a la Lista</button>
            </Link>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          {/* Use location.id */}
          <p><strong>ID:</strong> {location.id}</p>
          <p><strong>Nombre:</strong> {location.name}</p>
          {/* Display description instead of address */}
          <p><strong>Descripción:</strong> {location.description || 'N/A'}</p>
          {/* Access parent name assuming parent_location is an object with a name property, or null */}
          <p><strong>Ubicación Padre:</strong> {location.parent_location?.name || 'N/A'}</p>
          <p><strong>Capacidad de Almacenamiento:</strong> {location.storage_capacity !== undefined && location.storage_capacity !== null ? location.storage_capacity : 'N/A'}</p>
          <p><strong>Estado:</strong> {location.is_active ? 'Activa' : 'Inactiva'}</p>
           {/* Aquí podrías añadir listas de sub-ubicaciones o stock en esta ubicación */}
        </div>
      </div>
    </>
  );
}
