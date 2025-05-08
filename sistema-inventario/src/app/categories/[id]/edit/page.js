// app/categories/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getCategoryById, getCategories } from '../../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function EditCategoryPage() {
  const router = useRouter();
  const params = useParams();
  const categoryId = params.id ? parseInt(params.id, 10) : null;

  const [category, setCategory] = useState(undefined); // Almacena los datos originales
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [availableParents, setAvailableParents] = useState([]); // Lista de categorías para seleccionar como padre

  // Estado para el formulario
  const [formData, setFormData] = useState({
    name: '',
    parent_id: '',
    description: '',
  });
   const [formError, setFormError] = useState('');


  useEffect(() => {
    if (categoryId !== null && !isNaN(categoryId)) {
      setLoading(true);
      setError(null);

      // Cargar datos de la categoría a editar
      const foundCategory = getCategoryById(categoryId);

      if (foundCategory) {
          setCategory(foundCategory);
          // Precargar el formulario
          setFormData({
            name: foundCategory.name,
            parent_id: foundCategory.parent_id ? foundCategory.parent_id.toString() : '', // Convertir a string para select
            description: foundCategory.description || '',
          });
           setLoading(false);
      } else {
           setError(`Categoría con ID ${categoryId} no encontrada.`);
           setLoading(false);
      }

      // Cargar categorías disponibles para seleccionar como padre (excluir la categoría actual)
      const categories = getCategories().filter(cat => cat.category_id !== categoryId);
      setAvailableParents(categories);


      // En un sistema real:
      // fetch(`/api/categories/${categoryId}`).then(...)
      // fetch('/api/categories').then(...).then(allCats => setAvailableParents(allCats.filter(...)))
    } else {
         setError("ID de categoría inválido en la URL.");
         setLoading(false);
    }
  }, [categoryId]);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setFormError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError('');

    // --- Validación simple ---
    if (!formData.name) {
        setFormError('El nombre de la categoría es obligatorio.');
        return;
    }
    // --- Fin Validación simple ---

    console.log(`Datos a actualizar para categoría ID ${categoryId}:`, formData);
    // Lógica para enviar los datos actualizados a tu API
    // fetch(`/api/categories/${categoryId}`, {
    //    method: 'PUT',
    //    headers: { 'Content-Type': 'application/json' },
    //    body: JSON.stringify({
    //      ...formData,
    //      parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id, 10)
    //    }),
    // })
    // .then(...)


    alert(`Categoría ${category?.name} actualizada (simulado)`); // Simulación
    router.push(`/categories/${categoryId}`); // Redirigir a los detalles
  };

    if (loading) {
        return <div className="text-center">Cargando...</div>;
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

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
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="nameInput" className="form-label">Nombre de la Categoría</label>
                        <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required maxLength="100" />
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
                            {/* Mapear las categorías disponibles. Asegurarse de que la categoría actual no aparezca como opción padre */}
                            {availableParents.map(parentCat => (
                                <option key={parentCat.category_id} value={parentCat.category_id}>
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
                        <textarea className="form-control" id="descriptionTextarea" rows="3" name="description" value={formData.description} onChange={handleChange}></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Actualizar Categoría
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}