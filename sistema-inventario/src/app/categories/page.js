// app/categories/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { deleteCategory, getAllCategories } from '../../services/categoryService'; // Import from your service
import { useRouter } from 'next/navigation'; // Import useRouter for potential redirects/reloads

export default function CategoryListPage() {
  const router = useRouter();
  const [categories, setCategories] = useState([]);
  const [parentNames, setParentNames] = useState({}); // To store parent category names
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to fetch categories
  const fetchCategories = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getAllCategories();
      if (response && response.success) {
        const fetchedCategories = response.data;
        setCategories(fetchedCategories);

        // Build a map of category IDs to names for parent lookup
        const namesMap = fetchedCategories.reduce((acc, cat) => {
            // Corrected: Use cat.id for the key in the map
            acc[cat.id] = cat.name;
            return acc;
        }, {});
        setParentNames(namesMap);

      } else {
         // Handle API-specific success: false response structure
         setError(response?.message || 'Failed to fetch categories');
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError(err.message || 'An error occurred while fetching categories.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []); // Fetch categories on component mount

   const handleDelete = async (id) => {
       if (confirm(`¿Está seguro de eliminar la categoría con ID ${id}?`)) {
           try {
               // Call the delete service function
               const response = await deleteCategory(id);
               if (response && response.success) {
                   console.log(`Category ${id} deleted successfully`);
                   // Update the state to remove the deleted category
                   // Corrected: Filter using category.id
                   setCategories(categories.filter(category => category.id !== id));
                   // Also potentially update the parent names map if needed
               } else {
                  // Handle API-specific success: false response structure
                  setError(response?.message || `Failed to delete category ${id}`);
                  alert(response?.message || `Error al eliminar la categoría ${id}. Puede tener productos o subcategorías asociadas.`); // Show user-friendly message
               }
           } catch (err) {
               console.error(`Error deleting category ${id}:`, err);
               setError(err.message || `An error occurred while deleting category ${id}.`);
               alert(err.message || `Error al eliminar la categoría ${id}. Verifique si tiene productos o subcategorías asociadas.`); // Show user-friendly error
           }
       }
   };


  if (loading) {
    return <div className="text-center text-primary">Cargando categorías...</div>;
  }

   if (error) {
       return <div className="alert alert-danger">Error: {error}</div>;
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
            {categories.length === 0 ? (
                <tr>
                    <td colSpan="4" className="text-center">No se encontraron categorías.</td>
                </tr>
            ) : (
                categories.map(category => (
                // Corrected: Use category.id for the key
                <tr key={category.id}>
                    {/* Corrected: Display category.id */}
                    <td>{category.id}</td>
                    <td>{category.name}</td>
                    {/* Corrected: Use category.id to look up parent name if parent_id exists */}
                    <td>{category.parent_id ? parentNames[category.parent_id] || `ID: ${category.parent_id}` : 'N/A'}</td>
                    <td>
                    {/* Corrected: Use category.id in Link hrefs */}
                    <Link href={`/categories/${category.id}`} passHref >
                        <button type="button" className="btn btn-info btn-sm me-2">Ver</button>
                    </Link>
                    {/* Corrected: Use category.id in Link hrefs */}
                    <Link href={`/categories/${category.id}/edit`} passHref >
                        <button type="button" className="btn btn-warning btn-sm me-2">Editar</button>
                    </Link>
                    <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        // Corrected: Pass category.id to handleDelete
                        onClick={() => handleDelete(category.id)}
                    >
                        Eliminar
                    </button>
                    </td>
                </tr>
                ))
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}