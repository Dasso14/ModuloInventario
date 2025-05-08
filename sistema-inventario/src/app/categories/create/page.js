// app/categories/create/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createCategory, getAllCategories } from '../../../services/categoryService'; // Import from your service

export default function CreateCategoryPage() {
  const router = useRouter();
  const [availableParents, setAvailableParents] = useState([]); // List of categories for parent select
  const [loadingParents, setLoadingParents] = useState(true);

  const [formData, setFormData] = useState({
    name: '',
    parent_id: '', // Use string empty for the select value when no parent is chosen
    description: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);


  useEffect(() => {
      // Load available categories for parent selection
      const fetchParents = async () => {
          setLoadingParents(true);
          try {
              const response = await getAllCategories();
              if (response && response.success) {
                 // Filter out the category being created if it were an edit page
                 // For create, just use all categories as potential parents
                 setAvailableParents(response.data);
              } else {
                // Handle API success: false
                 console.error('Failed to fetch parent categories:', response?.message);
              }
          } catch (err) {
              console.error('Error fetching parent categories:', err);
          } finally {
              setLoadingParents(false);
          }
      };

      fetchParents();
  }, []); // Fetch categories on component mount


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setError(''); // Clear error when form changes
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // --- Simple Validation ---
    if (!formData.name.trim()) { // Use trim() to check for empty or whitespace-only name
        setError('El nombre de la categoría es obligatorio.');
        return;
    }
    // --- End Simple Validation ---

    setIsSubmitting(true); // Disable button while submitting

    // Prepare data for the API call
    const dataToSend = {
      ...formData,
      // Convert parent_id: "" to null for the backend if necessary
      // Your Flask API should handle this based on its expected input format.
      // Assuming "" or null are acceptable for no parent. Let's explicitly send null for ""
      parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id, 10),
       // Add user_id if your backend requires it for creation context
       // user_id: currentUser.id, // Example if you have logged-in user info
    };

    try {
        // Call the create service function
        const response = await createCategory(dataToSend);

        if (response && response.success) {
            console.log('Category created successfully:', response.data);
            // Redirect to the category list page
            router.push('/categories');
        } else {
             // Handle API-specific success: false response structure
             const errorMessage = response?.message || 'Failed to create category';
             setError(errorMessage);
             console.error('API Error creating category:', errorMessage);
        }

    } catch (err) {
        console.error('Error creating category:', err);
        setError(err.message || 'An error occurred while creating the category.');
    } finally {
        setIsSubmitting(false); // Re-enable button
    }
  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Crear Nueva Categoría</h1>
            <Link href="/categories" passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {error && <div className="alert alert-danger">{error}</div>}

                {loadingParents ? (
                    <div className="text-center text-primary">Cargando opciones de categorías padre...</div>
                ) : (
                     <form onSubmit={handleSubmit}>
                        <div className="mb-3">
                            <label htmlFor="nameInput" className="form-label">Nombre de la Categoría</label>
                            <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required />
                        </div>

                         <div className="mb-3">
                            <label htmlFor="parentSelect" className="form-label">Categoría Padre (Opcional)</label>
                            <select
                                className="form-select"
                                id="parentSelect"
                                name="parent_id"
                                value={formData.parent_id}
                                onChange={handleChange}
                            >
                                <option value="">Sin Categoría Padre</option>
                                {/* Map available categories */}
                                {availableParents.map(category => (
                                    <option key={category.id} value={category.id}>{category.name}</option>
                                ))}
                            </select>
                             <div className="form-text">
                               Seleccione una categoría si esta es una subcategoría.
                            </div>
                        </div>

                        <div className="mb-3">
                            <label htmlFor="descriptionTextarea" className="form-label">Descripción</label>
                            <textarea className="form-control" id="descriptionTextarea" rows="3" name="description" value={formData.description} onChange={handleChange}></textarea>
                        </div>

                        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                            {isSubmitting ? 'Guardando...' : 'Guardar Categoría'}
                        </button>
                    </form>
                )}
            </div>
        </div>
     </>
  );
}