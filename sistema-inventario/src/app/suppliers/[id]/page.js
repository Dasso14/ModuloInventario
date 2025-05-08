// app/suppliers/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getSupplierById } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function SupplierDetailPage() {
  const router = useRouter();
  const params = useParams();
  const supplierId = params.id ? parseInt(params.id, 10) : null;

  const [supplier, setSupplier] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    if (supplierId !== null && !isNaN(supplierId)) {
      setLoading(true);
      setError(null);
      
      // Realizar petición a la API real
      fetch(`/api/suppliers/${supplierId}`)
        .then(res => {
          if (!res.ok) {
            throw new Error(`Error: ${res.status} - ${res.statusText}`);
          }
          return res.json();
        })
        .then(response => {
          if (response.success) {
            setSupplier(response.data);
          } else {
            throw new Error(response.message || 'Error al obtener datos del proveedor');
          }
          setLoading(false);
        })
        .catch(err => {
          setError(err.message);
          setLoading(false);
        });
    } else {
      setError("ID de proveedor inválido en la URL.");
      setLoading(false);
    }
  }, [supplierId]);

  const handleDeleteSupplier = () => {
    // Mostrar confirmación antes de eliminar
    setShowDeleteConfirm(true);
  };

  const confirmDelete = () => {
    setLoading(true);
    fetch(`/api/suppliers/${supplierId}`, {
      method: 'DELETE',
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Error: ${res.status} - ${res.statusText}`);
        }
        return res.json();
      })
      .then(response => {
        if (response.success) {
          // Redireccionar a la lista de proveedores tras eliminar
          router.push('/suppliers');
        } else {
          throw new Error(response.message || 'Error al eliminar el proveedor');
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
        setShowDeleteConfirm(false);
      });
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  if (loading) {
    return (
      <div className="text-center p-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-2">Cargando datos del proveedor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger">
        <h4 className="alert-heading">Error</h4>
        <p>{error}</p>
        <hr />
        <Link href="/suppliers" passHref>
          <button className="btn btn-primary">Volver a la Lista de Proveedores</button>
        </Link>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="alert alert-warning">
        <h4 className="alert-heading">Proveedor no disponible</h4>
        <p>No se pudo encontrar la información del proveedor solicitado.</p>
        <hr />
        <Link href="/suppliers" passHref>
          <button className="btn btn-primary">Volver a la Lista de Proveedores</button>
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles del Proveedor: {supplier.name}</h1>
        <div>
          <Link href={`/suppliers/${supplierId}/edit`} passHref>
            <button type="button" className="btn btn-warning me-2">Editar</button>
          </Link>
          <button 
            type="button" 
            className="btn btn-danger me-2"
            onClick={handleDeleteSupplier}
          >
            Eliminar
          </button>
          <Link href="/suppliers" passHref>
            <button type="button" className="btn btn-secondary">Volver a la Lista</button>
          </Link>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="alert alert-danger mb-3">
          <h5>¿Está seguro que desea eliminar este proveedor?</h5>
          <p>Esta acción no se puede deshacer. Si el proveedor tiene productos asociados, no podrá ser eliminado.</p>
          <div className="d-flex gap-2">
            <button className="btn btn-danger" onClick={confirmDelete}>Confirmar Eliminación</button>
            <button className="btn btn-secondary" onClick={cancelDelete}>Cancelar</button>
          </div>
        </div>
      )}

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <div className="row">
            <div className="col-md-6">
              <p><strong>ID:</strong> {supplier.id}</p>
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
        </div>
      </div>

      {/* Información adicional - Si en el futuro implementas productos relacionados */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="mb-0">Productos Suministrados</h5>
        </div>
        <div className="card-body">
          {supplier.products && supplier.products.length > 0 ? (
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Precio</th>
                    <th>Stock</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {supplier.products.map(product => (
                    <tr key={product.id}>
                      <td>{product.id}</td>
                      <td>{product.name}</td>
                      <td>${product.price.toFixed(2)}</td>
                      <td>{product.stock}</td>
                      <td>
                        <Link href={`/products/${product.id}`} passHref>
                          <button className="btn btn-sm btn-info">Ver</button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted">Este proveedor no tiene productos asociados.</p>
          )}
        </div>
      </div>
    </>
  );
}