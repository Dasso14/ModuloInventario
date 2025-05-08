// app/suppliers/create/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function CreateSupplierPage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: '',
    contact_name: '',
    phone: '',
    email: '',
    address: '',
    tax_id: '',
  });
   const [error, setError] = useState('');


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
        setError('El nombre del proveedor es obligatorio.');
        return;
    }
    // --- Fin Validación simple ---


    console.log('Datos a enviar para crear proveedor:', formData);
    // Lógica para enviar datos a tu API para crear el proveedor
    // fetch('/api/suppliers', { method: 'POST', body: JSON.stringify(formData) })
    // .then(...)

    alert('Proveedor creado (simulado)'); // Simulación
    router.push('/suppliers'); // Redirigir a la lista de proveedores después de "crear"
  };

  return (
     <>
        <div className="d-flex justify-content-between align-items-center mb-3">
            <h1>Crear Nuevo Proveedor</h1>
            <Link href="/suppliers" passHref >
                 <button type="button" className="btn btn-secondary">Cancelar</button>
            </Link>
        </div>

        <div className="card">
            <div className="card-body">
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="nameInput" className="form-label">Nombre del Proveedor</label>
                        <input type="text" className="form-control" id="nameInput" name="name" value={formData.name} onChange={handleChange} required maxLength="255" />
                    </div>

                    <div className="row g-3 mb-3">
                        <div className="col-md-6">
                            <label htmlFor="contactNameInput" className="form-label">Nombre de Contacto</label>
                            <input type="text" className="form-control" id="contactNameInput" name="contact_name" value={formData.contact_name} onChange={handleChange} maxLength="255" />
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="phoneInput" className="form-label">Teléfono</label>
                            <input type="tel" className="form-control" id="phoneInput" name="phone" value={formData.phone} onChange={handleChange} maxLength="50" />
                        </div>
                    </div>

                    <div className="row g-3 mb-3">
                         <div className="col-md-6">
                            <label htmlFor="emailInput" className="form-label">Email</label>
                            <input type="email" className="form-control" id="emailInput" name="email" value={formData.email} onChange={handleChange} maxLength="100" />
                        </div>
                         <div className="col-md-6">
                            <label htmlFor="taxIdInput" className="form-label">RFC / Tax ID</label>
                            <input type="text" className="form-control" id="taxIdInput" name="tax_id" value={formData.tax_id} onChange={handleChange} maxLength="50" />
                        </div>
                    </div>


                    <div className="mb-3">
                        <label htmlFor="addressTextarea" className="form-label">Dirección</label>
                        <textarea className="form-control" id="addressTextarea" rows="3" name="address" value={formData.address} onChange={handleChange}></textarea>
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Guardar Proveedor
                    </button>
                </form>
            </div>
        </div>
     </>
  );
}