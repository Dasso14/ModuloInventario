// app/suppliers/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getSupplierById } from '../../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function EditSupplierPage() {
  const router = useRouter();
  const params = useParams();
  const supplierId = params.id ? parseInt(params.id, 10) : null;

  const [supplier, setSupplier] = useState(undefined); // Almacena los datos originales del proveedor
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Estado para el formulario (inicializará cuando se carguen los datos del proveedor)
  const [formData, setFormData] = useState({
    name: '',
    contact_name: '',
    phone: '',
    email: '',
    address: '',
    tax_id: '',
  });
   const [formError, setFormError] = useState(''); // Errores de validación del formulario


  useEffect(() => {
    if (supplierId !== null && !isNaN(supplierId)) {
      setLoading(true);
      setError(null);
      // Simular carga de datos
      const foundSupplier = getSupplierById(supplierId);

      if (foundSupplier) {
          setSupplier(foundSupplier);
          // Precargar el formulario con los datos existentes
          setFormData({
            name: foundSupplier.name,
            contact_name: foundSupplier.contact_name || '',
            phone: foundSupplier.phone || '',
            email: foundSupplier.email || '',
            address: foundSupplier.address || '',
            tax_id: foundSupplier.tax_id || '',
          });
           setLoading(false);
      } else {
           setError(`Proveedor con ID ${supplierId} no encontrado.`);
           setLoading(false);
      }

      // En un sistema real:
      // fetch(`/api/suppliers/${supplierId}`).then(...)
    } else {
         setError("ID de proveedor inválido en la URL.");
         setLoading(false);
    }
  }, [supplierId]); // Dependencia: recargar si cambia el ID en la URL


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setFormError(''); // Limpiar error al cambiar algo
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormError('');

    // --- Validación simple ---
    if (!formData.name) {
        setFormError('El nombre del proveedor es obligatorio.');
        return;
    }
    // --- Fin Validación simple ---

    console.log(`Datos a actualizar para proveedor ID ${supplierId}:`, formData);
    // Lógica para enviar los datos actualizados a tu API
    // fetch(`/api/suppliers/${supplierId}`, { method: 'PUT', body: JSON.stringify(formData) })
    // .then(...)

    alert(`Proveedor ${supplier?.name} actualizado (simulado)`); // Simulación
    router.push(`/suppliers/${supplierId}`); // Redirigir a los detalles del proveedor después de "actualizar"
  };

    if (loading) {
        return (
            <div className="text-center">
                Cargando...
            </div>
        );
    }

    if (error) {
        return <div className="alert alert-danger">{error}</div>;
    }

    if (!supplier) {
        return <div className="alert alert-warning">Proveedor no disponible.</div>;
    }


  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Editar Proveedor: {supplier.name}</h1>
            <Link href={`/suppliers/${supplier.supplier_id}`} passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {formError && <div className="alert alert-danger">{formError}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="nameInput" className="form-label">Nombre del Proveedor</label>
                        <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required />
                    </div>

                    <div className="row g-3 mb-3">
                        <div className="col-md-6">
                            <label htmlFor="contactNameInput" className="form-label">Nombre de Contacto</label>
                            <input type="text" className="form-control" id="contactNameInput" name="contact_name" value={formData.contact_name} onChange={handleChange} />
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="phoneInput" className="form-label">Teléfono</label>
                            <input type="tel" className="form-control" id="phoneInput" name="phone" value={formData.phone} onChange={handleChange} />
                        </div>
                    </div>

                     <div className="row g-3 mb-3">
                         <div className="col-md-6">
                            <label htmlFor="emailInput" className="form-label">Email</label>
                            <input type="email" className="form-control" id="emailInput" name="email" value={formData.email} onChange={handleChange} />
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="taxIdInput" className="form-label">RFC / Tax ID</label>
                            <input type="text" className="form-control" id="taxIdInput" name="tax_id" value={formData.tax_id} onChange={handleChange} />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label htmlFor="addressTextarea" className="form-label">Dirección</label>
                        <textarea className="form-control" id="addressTextarea" rows="3" name="address" value={formData.address} onChange={handleChange}></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Actualizar Proveedor
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}