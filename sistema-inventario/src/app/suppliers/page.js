// app/suppliers/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { toast } from 'react-hot-toast'; // Asegúrate de tener react-hot-toast instalado
import { getSuppliers } from '../../../lib/product-data'; // Ya no necesitas esta importación simulada

export default function SupplierListPage() {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estados para filtrado y paginación
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  const fetchSuppliers = async () => {
    setLoading(true);
    try {
      // Construir URL con parámetros de consulta para filtros, paginación y ordenación
      const queryParams = new URLSearchParams();
      if (searchTerm) queryParams.append('search', searchTerm);
      queryParams.append('page', currentPage.toString());
      queryParams.append('sort_by', sortField);
      queryParams.append('sort_dir', sortDirection);
      
      const response = await fetch(`/api/suppliers?${queryParams.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Error al cargar proveedores: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setSuppliers(result.data);
        // Si la API devuelve metadatos de paginación
        if (result.pagination) {
          setTotalPages(result.pagination.total_pages || 1);
        }
        setError(null);
      } else {
        throw new Error(result.message || 'Error desconocido al cargar proveedores');
      }
    } catch (err) {
      console.error('Error fetching suppliers:', err);
      setError(err.message);
      toast.error('Error al cargar los proveedores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, [searchTerm, currentPage, sortField, sortDirection]);

  const handleDelete = async (id) => {
    if (confirm(`¿Está seguro de eliminar el proveedor con ID ${id}?`)) {
      try {
        const response = await fetch(`/api/suppliers/${id}`, { 
          method: 'DELETE',
        });
        
        const result = await response.json();
        
        if (result.success) {
          // Actualizar la lista después de eliminar
          setSuppliers(suppliers.filter(supplier => supplier.id !== id));
          toast.success(`Proveedor ${id} eliminado correctamente`);
        } else {
          throw new Error(result.message || 'Error al eliminar el proveedor');
        }
      } catch (err) {
        console.error('Error deleting supplier:', err);
        toast.error(err.message || 'Error al eliminar el proveedor');
      }
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // Reiniciar a la primera página cuando se busca
    // fetchSuppliers se ejecutará debido al useEffect
  };

  const handleSort = (field) => {
    // Si es el mismo campo, invertir dirección, si no, ordenar ascendente
    setSortDirection(field === sortField && sortDirection === 'asc' ? 'desc' : 'asc');
    setSortField(field);
  };

  const renderSortIcon = (field) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  if (loading && suppliers.length === 0) {
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

      <div className="card mb-4">
        <div className="card-body">
          <form onSubmit={handleSearch} className="row g-3">
            <div className="col-md-8">
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por nombre, email o contacto..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button className="btn btn-outline-secondary" type="submit">
                  <i className="bi bi-search"></i> Buscar
                </button>
              </div>
            </div>
            <div className="col-md-4 d-flex justify-content-end">
              <button 
                type="button" 
                className="btn btn-outline-secondary"
                onClick={() => {
                  setSearchTerm('');
                  setCurrentPage(1);
                  setSortField('name');
                  setSortDirection('asc');
                }}
              >
                <i className="bi bi-x-circle me-1"></i> Limpiar filtros
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="table-responsive">
        <table className="table table-striped table-bordered table-hover">
          <thead className="table-light">
            <tr>
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
            {suppliers.length > 0 ? (
              suppliers.map(supplier => (
                <tr key={supplier.id}>
                  <td>{supplier.id}</td>
                  <td>{supplier.name}</td>
                  <td>{supplier.contact_name || 'N/A'}</td>
                  <td>{supplier.phone || 'N/A'}</td>
                  <td>{supplier.email || 'N/A'}</td>
                  <td className="text-center">
                    <div className="btn-group" role="group">
                      <Link href={`/suppliers/${supplier.id}`} passHref>
                        <button type="button" className="btn btn-info btn-sm">
                          <i className="bi bi-eye me-1"></i> Ver
                        </button>
                      </Link>
                      <Link href={`/suppliers/${supplier.id}/edit`} passHref>
                        <button type="button" className="btn btn-warning btn-sm">
                          <i className="bi bi-pencil me-1"></i> Editar
                        </button>
                      </Link>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(supplier.id)}
                      >
                        <i className="bi bi-trash me-1"></i> Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="text-center">
                  {loading ? "Cargando proveedores..." : "No se encontraron proveedores"}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      {totalPages > 1 && (
        <nav aria-label="Navegación de páginas">
          <ul className="pagination justify-content-center">
            <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage - 1)}>
                &laquo; Anterior
              </button>
            </li>
            
            {[...Array(totalPages).keys()].map(page => (
              <li key={page + 1} className={`page-item ${currentPage === page + 1 ? 'active' : ''}`}>
                <button className="page-link" onClick={() => handlePageChange(page + 1)}>
                  {page + 1}
                </button>
              </li>
            ))}
            
            <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => handlePageChange(currentPage + 1)}>
                Siguiente &raquo;
              </button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );
}