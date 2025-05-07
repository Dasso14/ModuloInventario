// app/suppliers/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getSuppliers } from '../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function SupplierListPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carga de datos
    const data = getSuppliers();
    setSuppliers(data);
    setLoading(false);
    // En un sistema real:
    // fetch('/api/suppliers')
    //   .then(res => res.json())
    //   .then(data => {
    //     setSuppliers(data);
    //     setLoading(false);
    //   });
  }, []);

   const handleDelete = (id) => {
       if (confirm(`¿Está seguro de eliminar el proveedor con ID ${id}? (Simulado)`)) {
           console.log(`Eliminando proveedor con ID: ${id} (Simulado)`);
           // Lógica de eliminación real:
           // fetch(`/api/suppliers/${id}`, { method: 'DELETE' })
           // .then(...)
           // Actualizar la lista después de eliminar (re-fetch o filtrar)
           setSuppliers(suppliers.filter(supplier => supplier.supplier_id !== id)); // Simulación de eliminación de la lista
       }
   };


  if (loading) {
    return <div className="text-center">Cargando...</div>; // Puedes usar un spinner de Bootstrap si quieres
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Lista de Proveedores</h1>
        <Link href="/suppliers/create" passHref >
           <button type="button" className="btn btn-primary">Crear Nuevo Proveedor</button>
        </Link>
      </div>

      {/* Aquí iría la barra de búsqueda/filtrado si la implementas */}

      <div className="table-responsive"> {/* Añadir responsive para tablas pequeñas */}
        <table className="table table-striped table-bordered table-hover">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Contacto</th>
              <th>Teléfono</th>
              <th>Email</th>
              {/* <th>Dirección</th> */}
              {/* <th>RFC/Tax ID</th> */}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {suppliers.map(supplier => (
              <tr key={supplier.supplier_id}>
                <td>{supplier.supplier_id}</td>
                <td>{supplier.name}</td>
                <td>{supplier.contact_name || 'N/A'}</td>
                <td>{supplier.phone || 'N/A'}</td>
                <td>{supplier.email || 'N/A'}</td>
                {/* <td>{supplier.address || 'N/A'}</td> */}
                {/* <td>{supplier.tax_id || 'N/A'}</td> */}
                <td>
                  <Link href={`/suppliers/${supplier.supplier_id}`} passHref >
                    <button type="button" className="btn btn-info btn-sm me-2">Ver</button>
                  </Link>
                   <Link href={`/suppliers/${supplier.supplier_id}/edit`} passHref >
                    <button type="button" className="btn btn-warning btn-sm me-2">Editar</button>
                  </Link>
                   <button
                       type="button"
                       className="btn btn-danger btn-sm"
                       onClick={() => handleDelete(supplier.supplier_id)}
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