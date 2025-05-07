// app/categories/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getCategoryById, getCategoryName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function CategoryDetailPage() {
  const params = useParams();
  const categoryId = params.id ? parseInt(params.id, 10) : null;

  const [category, setCategory] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (categoryId !== null && !isNaN(categoryId)) {
      setLoading(true);
      setError(null);
      // Simular carga de datos
      const foundCategory = getCategoryById(categoryId);

      if (foundCategory) {
          setCategory(foundCategory);
           setLoading(false);
      } else {
           setError(`Categoría con ID ${categoryId} no encontrada.`);
           setLoading(false);
      }

      // En un sistema real: fetch(`/api/categories/${categoryId}`).then(...)
    } else {
         setError("ID de categoría inválido en la URL.");
         setLoading(false);
    }
  }, [categoryId]);


    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    if (!category) {
        return <div className="alert alert-warning">Categoría no disponible.</div>;
    }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles de la Categoría: {category.name}</h1>
        <div>
           <Link href={`/categories/${category.category_id}/edit`} passHref >
              <button type="button" className="btn btn-warning me-2">Editar</button>
            </Link>
            <Link href="/categories" passHref >
              <button type="button" className="btn btn-secondary">Volver a la Lista</button>
            </Link>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <p><strong>ID:</strong> {category.category_id}</p>
          <p><strong>Nombre:</strong> {category.name}</p>
          {/* Usamos la función getCategoryName para mostrar el nombre del padre si existe */}
          <p><strong>Categoría Padre:</strong> {category.parent_id ? getCategoryName(category.parent_id) : 'N/A'}</p>
          <p><strong>Descripción:</strong> {category.description || 'N/A'}</p>
           {/* Aquí podrías añadir listas de subcategorías o productos asociados */}
        </div>
      </div>
    </>
  );
}