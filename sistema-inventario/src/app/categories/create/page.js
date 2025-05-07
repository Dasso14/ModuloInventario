// app/categories/create/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';    
import { getCategories } from '../../../../lib/product-data'; // Datos para el select padre

export default function CreateCategoryPage() {
  const router = useRouter();
  const [availableParents, setAvailableParents] = useState([]); // Lista de categorías para seleccionar como padre

  const [formData, setFormData] = useState({
    name: '',
    parent_id: '', // Usar string vacío para el select
    description: '',
  });
    const [error, setError] = useState('');


  useEffect(() => {
      // Cargar categorías disponibles para seleccionar como padre
      const categories = getCategories();
      setAvailableParents(categories);
      // En un sistema real: fetch('/api/categories').then(...)
  }, []);


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
     setError('');

    // --- Validación simple ---
    if (!formData.name) {
        setError('El nombre de la categoría es obligatorio.');
        return;
    }
    // --- Fin Validación simple ---

    console.log('Datos a enviar para crear categoría:', formData);
    // Lógica para enviar datos a tu API para crear la categoría
    // fetch('/api/categories', {
    //    method: 'POST',
    //    headers: { 'Content-Type': 'application/json' },
    //    body: JSON.stringify({
    //      ...formData,
    //      parent_id: formData.parent_id === '' ? null : parseInt(formData.parent_id, 10) // Convertir a null si no se seleccionó padre
    //    }),
    // })
    // .then(...)

    alert('Categoría creada (simulado)'); // Simulación
    router.push('/categories'); // Redirigir a la lista de categorías después de "crear"
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
                            {/* Mapear las categorías disponibles. Evitar que una categoría sea padre de sí misma. */}
                            {availableParents.map(category => (
                                <option key={category.category_id} value={category.category_id}>{category.name}</option>
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

                    <button type="submit" className="btn btn-primary">
                        Guardar Categoría
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}