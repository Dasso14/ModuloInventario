// app/categories/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
// Import from your service
import { getCategoryById, getAllCategories } from '../../../services/categoryService';

export default function CategoryDetailPage() {
  const params = useParams();
  // Ensure categoryId is a number
  const categoryId = params.id ? parseInt(params.id, 10) : null;

  const [category, setCategory] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [parentNames, setParentNames] = useState({}); // To store parent category names
  const [loadingParents, setLoadingParents] = useState(true);


  useEffect(() => {
    const fetchData = async () => {
        if (categoryId === null || isNaN(categoryId)) {
            setError("ID de categoría inválido en la URL.");
            setLoading(false);
             setLoadingParents(false);
            return;
        }

        setLoading(true);
        setError(null);
        setLoadingParents(true);

        // Fetch the specific category
        try {
            const categoryResponse = await getCategoryById(categoryId);
            if (categoryResponse && categoryResponse.success) {
                setCategory(categoryResponse.data);
                 setLoading(false);
            } else {
                 setError(categoryResponse?.message || `Failed to fetch category with ID ${categoryId}`);
                 setLoading(false);
                 // Do not return here, proceed to fetch parents even if category fetch failed
            }
        } catch (err) {
            console.error(`Error fetching category ${categoryId}:`, err);
            setError(err.message || `An error occurred while fetching category ${categoryId}.`);
            setLoading(false);
             // Do not return here
        }

         // Fetch all categories to build parent name map
         try {
            const parentsResponse = await getAllCategories();
             if (parentsResponse && parentsResponse.success) {
                const namesMap = parentsResponse.data.reduce((acc, cat) => {
                    acc[cat.category_id] = cat.name;
                    return acc;
                }, {});
                setParentNames(namesMap);
             } else {
                 console.error('Failed to fetch all categories for parent names:', parentsResponse?.message);
             }
         } catch (err) {
             console.error('Error fetching all categories for parent names:', err);
         } finally {
            setLoadingParents(false);
         }
    };

    fetchData();

  }, [categoryId]); // Effect depends on categoryId


    // Show loading states for initial data fetch
    if (loading || loadingParents) { // Show loading while either category or parents are loading
        return <div className="text-center text-primary">Cargando detalles de la categoría...</div>;
    }

    // Show error if initial fetch failed
    if (error) {
        return <div className="alert alert-danger">Error: {error}</div>;
    }

    // Show message if category data is somehow missing after loading
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
          {/* Use the parentNames map to display the parent name */}
          <p><strong>Categoría Padre:</strong> {category.parent_id ? parentNames[category.parent_id] || `ID: ${category.parent_id}` : 'N/A'}</p>
          <p><strong>Descripción:</strong> {category.description || 'N/A'}</p>
           {/* Aquí podrías añadir listas de subcategorías o productos asociados */}
        </div>
      </div>
    </>
  );
}