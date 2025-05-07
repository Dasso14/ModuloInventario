// app/locations/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getLocations, getLocationName } from '../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function LocationListPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carga de datos
    const data = getLocations();
    setLocations(data);
    setLoading(false);
    // En un sistema real: fetch('/api/locations').then(...)
  }, []);

    const handleDelete = (id) => {
       if (confirm(`¿Está seguro de eliminar la ubicación con ID ${id}? (Simulado)`)) {
           console.log(`Eliminando ubicación con ID: ${id} (Simulado)`);
           // Lógica de eliminación real: fetch(`/api/locations/${id}`, { method: 'DELETE' }).then(...)
           setLocations(locations.filter(location => location.location_id !== id)); // Simulación
       }
   };


  if (loading) {
    return <div className="text-center">Cargando...</div>;
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
              <tr key={location.location_id}>
                <td>{location.location_id}</td>
                <td>{location.name}</td>
                 {/* Usamos la función getLocationName para mostrar el nombre del padre */}
                <td>{location.parent_location ? getLocationName(location.parent_location) : 'N/A'}</td>
                 <td>{location.storage_capacity !== undefined && location.storage_capacity !== null ? location.storage_capacity : 'N/A'}</td>
                 <td>{location.is_active ? 'Sí' : 'No'}</td>
                 {/* <td>{location.address || 'N/A'}</td> */}
                {/* <td>{location.description || 'N/A'}</td> */}
                <td>
                  <Link href={`/locations/${location.location_id}`} passHref >
                    <button type="button" className="btn btn-info btn-sm me-2">Ver</button>
                  </Link>
                   <Link href={`/locations/${location.location_id}/edit`} passHref >
                    <button type="button" className="btn btn-warning btn-sm me-2">Editar</button>
                  </Link>
                   <button
                       type="button"
                       className="btn btn-danger btn-sm"
                       onClick={() => handleDelete(location.location_id)}
                   >
                       Eliminar
                   </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}