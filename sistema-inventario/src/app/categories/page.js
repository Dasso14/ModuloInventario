// app/categories/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getCategories, getCategoryName } from '../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function CategoryListPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carga de datos
    const data = getCategories();
    setCategories(data);
    setLoading(false);
    // En un sistema real: fetch('/api/categories').then(...)
  }, []);

    const handleDelete = (id) => {
       if (confirm(`¿Está seguro de eliminar la categoría con ID ${id}? (Simulado)`)) {
           console.log(`Eliminando categoría con ID: ${id} (Simulado)`);
           // Lógica de eliminación real: fetch(`/api/categories/${id}`, { method: 'DELETE' }).then(...)
           setCategories(categories.filter(category => category.category_id !== id)); // Simulación
       }
   };


  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Lista de Categorías</h1>
        <Link href="/categories/create" passHref >
           <button type="button" className="btn btn-primary">Crear Nueva Categoría</button>
        </Link>
      </div>

      {/* Implementar vista de árbol si se desea mostrar jerarquía */}

      <div className="table-responsive">
        <table className="table table-striped table-bordered table-hover">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Categoría Padre</th>
              {/* <th>Descripción</th> */}
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(category => (
              <tr key={category.category_id}>
                <td>{category.category_id}</td>
                <td>{category.name}</td>
                {/* Usamos la función getCategoryName para mostrar el nombre del padre */}
                <td>{category.parent_id ? getCategoryName(category.parent_id) : 'N/A'}</td>
                {/* <td>{category.description || 'N/A'}</td> */}
                <td>
                  <Link href={`/categories/${category.category_id}`} passHref >
                    <button type="button" className="btn btn-info btn-sm me-2">Ver</button>
                  </Link>
                   <Link href={`/categories/${category.category_id}/edit`} passHref >
                    <button type="button" className="btn btn-warning btn-sm me-2">Editar</button>
                  </Link>
                   <button
                       type="button"
                       className="btn btn-danger btn-sm"
                       onClick={() => handleDelete(category.category_id)}
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