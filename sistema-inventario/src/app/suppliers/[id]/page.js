// app/suppliers/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation'; // Importar useRouter
import Link from 'next/link';
// Importamos las funciones del nuevo servicio
import { getSupplierById, deleteSupplier } from '../../../services/supplierService'; // Ajusta la ruta si es necesario

export default function SupplierDetailPage() {
  const router = useRouter(); // Inicializar useRouter
  const params = useParams();
  const supplierId = params.id ? parseInt(params.id, 10) : null;

  const [supplier, setSupplier] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const fetchSupplier = async () => {
      if (supplierId !== null && !isNaN(supplierId)) {
        setLoading(true);
        setError(null);
        try {
          // Usar la función del servicio para obtener el proveedor
          const result = await getSupplierById(supplierId);

          // Asumiendo que el servicio devuelve { success: true, data: {...} }
          if (result && result.success) {
            setSupplier(result.data);
          } else {
            // Manejar caso donde success es false o no se encuentra el proveedor
            setError(result?.message || `Proveedor con ID ${supplierId} no encontrado.`);
          }
        } catch (err) {
          // Manejar errores de red o del servicio
          setError(`Error al cargar proveedor: ${err.message}`);
        } finally {
          setLoading(false);
        }
      } else {
        setError("ID de proveedor inválido en la URL.");
        setLoading(false);
      }
    };

    fetchSupplier();
  }, [supplierId]); // Dependencia: recargar si cambia el ID en la URL

  const handleDeleteSupplier = () => {
    // Mostrar confirmación antes de eliminar
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    setLoading(true);
    setShowDeleteConfirm(false); // Ocultar el cuadro de confirmación al iniciar la eliminación

    try {
      // Usar la función del servicio para eliminar el proveedor
      const result = await deleteSupplier(supplierId);

      // Asumiendo que el servicio devuelve { success: true, message: "..." }
      if (result && result.success) {
        console.log('Proveedor eliminado exitosamente', result.message);
        // Redireccionar a la lista de proveedores tras eliminar
        router.push('/suppliers');
      } else {
        // Manejar caso donde success es false
        setError(result?.message || 'Error al eliminar el proveedor.');
      }
    } catch (err) {
      // Manejar errores de red o del servicio
      setError(`Error en la comunicación con el servidor al eliminar: ${err.message}`);
    } finally {
      setLoading(false); // Ocultar estado de carga
    }
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
        <p className="mt-2">{showDeleteConfirm ? 'Eliminando proveedor...' : 'Cargando datos del proveedor...'}</p> {/* Mensaje más específico */}
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
    // Este caso debería ser cubierto por el error al no encontrar el proveedor,
    // pero lo mantenemos como fallback.
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
            disabled={loading} // Deshabilitar botón mientras carga
          >
            Eliminar
          </button>
          <Link href="/suppliers" passHref>
            <button type="button" className="btn btn-secondary" disabled={loading}>Volver a la Lista</button> {/* Deshabilitar botón mientras carga */}
          </Link>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="alert alert-danger mb-3">
          <h5>¿Está seguro que desea eliminar este proveedor?</h5>
          <p>Esta acción no se puede deshacer. Si el proveedor tiene productos asociados, no podrá ser eliminado.</p>
          <div className="d-flex gap-2">
            <button className="btn btn-danger" onClick={confirmDelete} disabled={loading}>Confirmar Eliminación</button> {/* Deshabilitar mientras elimina */}
            <button className="btn btn-secondary" onClick={cancelDelete} disabled={loading}>Cancelar</button> {/* Deshabilitar mientras elimina */}
          </div>
        </div>
      )}

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <div className="row">
            <div className="col-md-6">
              <p><strong>ID:</strong> {supplier.id}</p> {/* Asegúrate de usar supplier.id si es el nombre de la propiedad */}
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
          {/* Asumiendo que la API devuelve una propiedad 'products' que es un array */}
          {supplier.products && Array.isArray(supplier.products) && supplier.products.length > 0 ? (
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
                      <td>${product.name}</td> {/* Corregido: Usar product.name */}
                      <td>${typeof product.price === 'number' ? product.price.toFixed(2) : product.price}</td> {/* Asegurar formato de precio */}
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