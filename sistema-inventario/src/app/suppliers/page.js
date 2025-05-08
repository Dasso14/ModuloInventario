// app/suppliers/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { toast } from 'react-hot-toast';
// Importamos las funciones del servicio
import { getAllSuppliers, deleteSupplier } from '../../services/supplierService'; // Ajusta la ruta si es necesario

export default function SupplierListPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Estados para paginación y ordenación (se mantienen)
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  const fetchSuppliers = async () => {
    setLoading(true);
    setError(null); // Limpiar error previo
    try {
      // Construir parámetros de consulta SOLO para paginación y ordenación
      const queryParams = new URLSearchParams();
      // Eliminamos: if (searchTerm) queryParams.append('search', searchTerm);
      queryParams.append('page', currentPage.toString());
      queryParams.append('sort_by', sortField);
      queryParams.append('sort_dir', sortDirection);

      const queryString = '?' + queryParams.toString();

      // Usar la función del servicio para obtener los proveedores
      // Asumimos que el servicio devuelve una respuesta con { success: boolean, data: [...], pagination?: {...}, message?: string }
      const result = await getAllSuppliers(queryString);

      if (result && result.success) {
        setSuppliers(result.data);
        if (result.pagination) {
          setTotalPages(result.pagination.total_pages || 1);
        } else {
          // Si la API no devuelve paginación, asumimos que es una sola página
          setTotalPages(1);
        }
        setError(null);
      } else {
        // Manejar caso donde success es false
        throw new Error(result?.message || 'Error desconocido al cargar proveedores');
      }
    } catch (err) {
      console.error('Error fetching suppliers:', err);
      setError(err.message);
      toast.error('Error al cargar los proveedores');
      setSuppliers([]);
      setTotalPages(1); // Reset pagination on error
    } finally {
      setLoading(false);
    }
  };

  // Este useEffect se dispara CUANDO cambian los parámetros que afectan la API
  // Eliminamos 'searchTerm' de las dependencias
  useEffect(() => {
    fetchSuppliers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, sortField, sortDirection]); // Dependencias actualizadas

  const handleDelete = async (id) => {
    if (confirm(`¿Está seguro de eliminar el proveedor con ID ${id}?`)) {
      // No seteamos loading a true globalmente para no bloquear toda la UI,
      // podrías manejar un estado por fila si quieres mostrar un spinner individual.
      try {
        const result = await deleteSupplier(id);

        if (result && result.success) {
          // Actualizar la lista después de eliminar sin recargar completamente
          setSuppliers(suppliers.filter(supplier => supplier.id !== id));
          toast.success(`Proveedor ${id} eliminado correctamente`);
           // Opcional: Refetch si la eliminación puede afectar la paginación (ej. última página)
           // fetchSuppliers();
        } else {
           const errorMessage = result?.message || 'Error al eliminar el proveedor';
           throw new Error(errorMessage);
        }
      } catch (err) {
        console.error('Error deleting supplier:', err);
        toast.error(err.message || 'Error al eliminar el proveedor');
      }
    }
  };

  // Eliminamos handleSearchSubmit y handleInputChange

  const handleSort = (field) => {
    // Si es el mismo campo, invertir dirección, si no, ordenar ascendente
    setSortDirection(field === sortField && sortDirection === 'asc' ? 'desc' : 'asc');
    setSortField(field);
    setCurrentPage(1); // Reiniciar a la primera página al cambiar la ordenación
  };

  const renderSortIcon = (field) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages && !loading) { // Prevenir cambio de página si está cargando
      setCurrentPage(newPage);
    }
  };

   // Mostrar un spinner si está cargando Y la lista está vacía
  if (loading && suppliers.length === 0 && !error) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '300px' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }


  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Lista de Proveedores</h1>
        <Link href="/suppliers/create" passHref>
          <button type="button" className="btn btn-primary">
            <i className="bi bi-plus-circle me-2"></i>Crear Nuevo Proveedor
          </button>
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Eliminamos el card con el formulario de búsqueda */}
      {/*
      <div className="card mb-4">
        <div className="card-body">
           ... contenido del formulario de búsqueda ...
        </div>
      </div>
      */}

      {loading && suppliers.length > 0 && ( // Mostrar spinner pequeño si ya hay datos pero está recargando (ej. paginación, ordenación)
         <div className="text-center mb-3">
             <div className="spinner-border spinner-border-sm text-primary" role="status">
                <span className="visually-hidden">Cargando...</span>
             </div>
             <span className="ms-2 text-muted">Actualizando lista...</span>
         </div>
      )}

      {/* Mensaje si no hay proveedores después de cargar y no hay error */}
      {/* Modificado para reflejar que no hay filtros */}
      {!loading && !error && suppliers.length === 0 && (
           <div className="alert alert-info text-center" role="alert">
               No se encontraron proveedores.
           </div>
      )}


      {/* La tabla solo se muestra si hay proveedores */}
      {suppliers.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped table-bordered table-hover">
            <thead className="table-light">
              <tr>
                {/* Las cabeceras para ordenar se mantienen */}
                <th onClick={() => handleSort('id')} style={{ cursor: 'pointer' }}>
                  ID {renderSortIcon('id')}
                </th>
                <th onClick={() => handleSort('name')} style={{ cursor: 'pointer' }}>
                  Nombre {renderSortIcon('name')}
                </th>
                <th onClick={() => handleSort('contact_name')} style={{ cursor: 'pointer' }}>
                  Contacto {renderSortIcon('contact_name')}
                </th>
                <th onClick={() => handleSort('phone')} style={{ cursor: 'pointer' }}>
                  Teléfono {renderSortIcon('phone')}
                </th>
                <th onClick={() => handleSort('email')} style={{ cursor: 'pointer' }}>
                  Email {renderSortIcon('email')}
                </th>
                <th className="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {suppliers.map(supplier => (
                  <tr key={supplier.id}>
                    <td>{supplier.id}</td>
                    <td>{supplier.name}</td>
                    <td>{supplier.contact_name || 'N/A'}</td>
                    <td>{supplier.phone || 'N/A'}</td>
                    <td>{supplier.email || 'N/A'}</td>
                    <td className="text-center">
                      <div className="btn-group" role="group">
                        <Link href={`/suppliers/${supplier.id}`} passHref>
                          <button type="button" className="btn btn-info btn-sm" disabled={loading}>
                            <i className="bi bi-eye me-1"></i> Ver
                          </button>
                        </Link>
                        <Link href={`/suppliers/${supplier.id}/edit`} passHref>
                          <button type="button" className="btn btn-warning btn-sm" disabled={loading}>
                            <i className="bi bi-pencil me-1"></i> Editar
                          </button>
                        </Link>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(supplier.id)}
                          disabled={loading} // Deshabilitar botón de eliminar mientras carga la lista principal
                        >
                          <i className="bi bi-trash me-1"></i> Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        </div>
      )}


      {/* Paginación solo se muestra si hay más de 1 página */}
      {totalPages > 1 && (
        <nav aria-label="Navegación de páginas" className="mt-4">
          <ul className="pagination justify-content-center">
            <li className={`page-item ${currentPage === 1 || loading ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1 || loading} aria-label="Anterior">
                &laquo; Anterior
              </button>
            </li>

            {/* Generar botones de página dinámicamente */}
            {[...Array(totalPages).keys()].map(page => (
              <li key={page + 1} className={`page-item ${currentPage === page + 1 ? 'active' : ''} ${loading ? 'disabled' : ''}`}>
                <button className="page-link" onClick={() => handlePageChange(page + 1)} disabled={loading}>
                  {page + 1}
                </button>
              </li>
            ))}

            <li className={`page-item ${currentPage === totalPages || loading ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages || loading} aria-label="Siguiente">
                Siguiente &raquo;
              </button>
            </li>
          </ul>
        </nav>
      )}
       {/* Agregar información sobre resultados si no hay error y no está cargando después de la primera carga */}
       {!loading && !error && suppliers.length > 0 && (
           <div className="text-center mt-3 text-muted">
               Mostrando {suppliers.length} de {totalPages} páginas encontradas.
           </div>
       )}
    </div>
  );
}
