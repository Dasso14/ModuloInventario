// app/locations/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getLocationById, getLocationName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function LocationDetailPage() {
  const params = useParams();
  const locationId = params.id ? parseInt(params.id, 10) : null;

  const [location, setLocation] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (locationId !== null && !isNaN(locationId)) {
      setLoading(true);
      setError(null);
      // Simular carga de datos
      const foundLocation = getLocationById(locationId);

      if (foundLocation) {
          setLocation(foundLocation);
           setLoading(false);
      } else {
           setError(`Ubicación con ID ${locationId} no encontrada.`);
           setLoading(false);
      }

      // En un sistema real: fetch(`/api/locations/${locationId}`).then(...)
    } else {
         setError("ID de ubicación inválido en la URL.");
         setLoading(false);
    }
  }, [locationId]);


    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    if (!location) {
        return <div className="alert alert-warning">Ubicación no disponible.</div>;
    }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles de la Ubicación: {location.name}</h1>
        <div>
           <Link href={`/locations/${location.location_id}/edit`} passHref >
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
          <p><strong>ID:</strong> {location.location_id}</p>
          <p><strong>Nombre:</strong> {location.name}</p>
          <p><strong>Dirección:</strong> {location.address || 'N/A'}</p>
          {/* Usamos la función getLocationName para mostrar el nombre del padre si existe */}
          <p><strong>Ubicación Padre:</strong> {location.parent_location ? getLocationName(location.parent_location) : 'N/A'}</p>
          <p><strong>Capacidad de Almacenamiento:</strong> {location.storage_capacity !== undefined && location.storage_capacity !== null ? location.storage_capacity : 'N/A'}</p>
          <p><strong>Descripción:</strong> {location.description || 'N/A'}</p>
          <p><strong>Estado:</strong> {location.is_active ? 'Activa' : 'Inactiva'}</p>
           {/* Aquí podrías añadir listas de sub-ubicaciones o stock en esta ubicación */}
        </div>
      </div>
    </>
  );
}