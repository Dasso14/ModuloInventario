// app/suppliers/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getSupplierById } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function SupplierDetailPage() {
  const params = useParams();
  const supplierId = params.id ? parseInt(params.id, 10) : null;

  const [supplier, setSupplier] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (supplierId !== null && !isNaN(supplierId)) {
      setLoading(true);
      setError(null);
      // Simular carga de datos
      const foundSupplier = getSupplierById(supplierId);

      if (foundSupplier) {
          setSupplier(foundSupplier);
           setLoading(false);
      } else {
           setError(`Proveedor con ID ${supplierId} no encontrado.`);
           setLoading(false);
      }

      // En un sistema real:
      // fetch(`/api/suppliers/${supplierId}`)
      // .then(res => { ... })
      // .then(data => { setSupplier(data); setLoading(false); })
      // .catch(err => { setError(err.message); setLoading(false); });
    } else {
         setError("ID de proveedor inválido en la URL.");
         setLoading(false);
    }
  }, [supplierId]);


    if (loading) {
        return (
            <div className="text-center">
                {/* Puedes usar un spinner de Bootstrap */}
                Cargando...
            </div>
        );
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    if (!supplier) {
        return <div className="alert alert-warning">Proveedor no disponible.</div>;
    }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles del Proveedor: {supplier.name}</h1>
        <div>
           <Link href={`/suppliers/${supplier.supplier_id}/edit`} passHref >
              <button type="button" className="btn btn-warning me-2">Editar</button>
            </Link>
            <Link href="/suppliers" passHref >
              <button type="button" className="btn btn-secondary">Volver a la Lista</button>
            </Link>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <div className="row">
            <div className="col-md-6">
              <p><strong>ID:</strong> {supplier.supplier_id}</p>
              <p><strong>Nombre:</strong> {supplier.name}</p>
              <p><strong>Nombre de Contacto:</strong> {supplier.contact_name || 'N/A'}</p>
            </div>
            <div className="col-md-6">
              <p><strong>Teléfono:</strong> {supplier.phone || 'N/A'}</p>
              <p><strong>Email:</strong> {supplier.email || 'N/A'}</p>
              <p><strong>RFC / Tax ID:</strong> {supplier.tax_id || 'N/A'}</p>
            </div>
          </div>
           <div className="row mt-3">
               <div className="col-12">
                    <p><strong>Dirección:</strong> {supplier.address || 'N/A'}</p>
               </div>
           </div>
           {/* Aquí podrías añadir listas de productos asociados, etc. */}
        </div>
      </div>
    </>
  );
}