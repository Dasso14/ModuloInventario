// app/categories/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
// Import from your service
import { getCategoryById, getAllCategories, updateCategory } from '../../../../services/categoryService';

export default function EditCategoryPage() {
  const router = useRouter();
  const params = useParams();
  // Ensure categoryId is a number, handle potential null/undefined from params
  const categoryId = params.id ? parseInt(params.id, 10) : null;

  const [category, setCategory] = useState(undefined); // Stores original fetched data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [availableParents, setAvailableParents] = useState([]); // List of categories for parent select
  const [loadingParents, setLoadingParents] = useState(true);

  // State for the form data, initialized empty
  const [formData, setFormData] = useState({
    name: '',
    parent_id: '', // Use string empty for the select value when no parent is chosen
    description: '',
  });
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);


  useEffect(() => {
    // Fetch category data and available parents concurrently
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


        try {
            // Fetch the specific category
            const categoryResponse = await getCategoryById(categoryId);
            if (categoryResponse && categoryResponse.success) {
                const fetchedCategory = categoryResponse.data;
                setCategory(fetchedCategory);
                // Pre-fill the form with fetched data
                setFormData({
                    name: fetchedCategory.name,
                    parent_id: fetchedCategory.parent_id ? fetchedCategory.parent_id.toString() : '', // Convert to string for select
                    description: fetchedCategory.description || '',
                });
                 setLoading(false);
            } else {
                 // Handle API-specific success: false
                 setError(categoryResponse?.message || `Failed to fetch category with ID ${categoryId}`);
                 setLoading(false);
                 return; // Stop if category not found/failed to fetch
            }

        } catch (err) {
            console.error(`Error fetching category ${categoryId}:`, err);
            setError(err.message || `An error occurred while fetching category ${categoryId}.`);
            setLoading(false);
            return; // Stop if error fetching category
        }

        // Fetch all categories for the parent dropdown
         try {
            const parentsResponse = await getAllCategories();
             if (parentsResponse && parentsResponse.success) {
                // Filter out the category being edited from the parent options
                const filteredParents = parentsResponse.data.filter(cat => cat.category_id !== categoryId);
                setAvailableParents(filteredParents);
             } else {
                console.error('Failed to fetch parent categories:', parentsResponse?.message);
                // Still allow editing even if parent list fails, just the dropdown will be empty/broken
             }
         } catch (err) {
            console.error('Error fetching parent categories:', err);
             // Still allow editing even if parent list fails
         } finally {
             setLoadingParents(false);
         }
    };

    fetchData();

  }, [categoryId]); // Effect depends on categoryId


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setFormError(''); // Clear form error when form changes
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // --- Simple Validation ---
    if (!formData.name.trim()) {
        setFormError('El nombre de la categoría es obligatorio.');
        return;
    }
    // --- End Simple Validation ---

     if (categoryId === null || isNaN(categoryId)) {
        setFormError("No se puede actualizar, ID de categoría inválido.");
        return;
    }

    setIsSubmitting(true); // Disable button while submitting

    // Prepare data for the API call
    const dataToSend = {
      ...formData,
      // Convert parent_id: "" to null for the backend if necessary
      parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id, 10),
       // Add user_id if your backend requires it for update context
       // user_id: currentUser.id, // Example if you have logged-in user info
    };

    try {
        // Call the update service function
        const response = await updateCategory(categoryId, dataToSend);

        if (response && response.success) {
            console.log(`Category ${categoryId} updated successfully:`, response.data);
             alert(`Categoría ${response.data.name} actualizada`); // Success message
            // Redirect to the category details page
            router.push(`/categories/${categoryId}`);
        } else {
             // Handle API-specific success: false response structure
             const errorMessage = response?.message || `Failed to update category ${categoryId}`;
             setFormError(errorMessage);
             console.error('API Error updating category:', errorMessage);
             alert(`Error al actualizar: ${errorMessage}`); // Show user-friendly error
        }

    } catch (err) {
        console.error(`Error updating category ${categoryId}:`, err);
        setFormError(err.message || `An error occurred while updating category ${categoryId}.`);
        alert(`Error al actualizar: ${err.message || 'Ocurrió un error'}`); // Show user-friendly error
    } finally {
        setIsSubmitting(false); // Re-enable button
    }
  };

    // Show loading states for initial data fetch
    if (loading) {
        return <div className="text-center text-primary">Cargando datos de la categoría...</div>;
    }

    // Show error if initial fetch failed
    if (error) {
        return <div className="alert alert-danger">Error: {error}</div>;
    }

     // Show message if category data is somehow missing after loading
     if (!category) {
        return <div className="alert alert-warning">Categoría no disponible para editar.</div>;
    }


  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Editar Categoría: {category.name}</h1>
            <Link href={`/categories/${category.category_id}`} passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                 {formError && <div className="alert alert-danger">{formError}</div>}

                 {/* Only show form if parent categories are loaded, or handle loading state inside form */}
                 {loadingParents ? (
                     <div className="text-center text-primary">Cargando opciones de categorías padre...</div>
                 ) : (
                     <form onSubmit={handleSubmit}>
                         <div className="mb-3">
                             <label htmlFor="nameInput" className="form-label">Nombre de la Categoría</label>
                             <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required disabled={isSubmitting}/>
                         </div>

                          <div className="mb-3">
                             <label htmlFor="parentSelect" className="form-label">Categoría Padre (Opcional)</label>
                             <select
                                 className="form-select"
                                 id="parentSelect"
                                 name="parent_id"
                                 value={formData.parent_id}
                                 onChange={handleChange}
                                 disabled={isSubmitting || loadingParents}
                             >
                                 <option value="">Sin Categoría Padre</option>
                                 {/* Map available categories */}
                                 {availableParents.map(parentCat => (
                                     <option key={parentCat.id} value={parentCat.id}>
                                         {parentCat.name}
                                     </option>
                                 ))}
                             </select>
                              <div className="form-text">
                                Seleccione una categoría si esta es una subcategoría. No se puede seleccionar a sí misma.
                             </div>
                         </div>

                         <div className="mb-3">
                             <label htmlFor="descriptionTextarea" className="form-label">Descripción</label>
                             <textarea className="form-control" id="descriptionTextarea" rows="3" name="description" value={formData.description} onChange={handleChange} disabled={isSubmitting}></textarea>
                         </div>

                         <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                             {isSubmitting ? 'Actualizando...' : 'Actualizar Categoría'}
                         </button>
                     </form>
                 )}
            </div>
        </div>
     </>
  );
}