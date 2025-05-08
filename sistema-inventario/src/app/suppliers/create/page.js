// app/suppliers/create/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast'; 
import { createSupplier } from '../../../lib/supplier-data'; // Importamos la función que creamos

export default function CreateSupplierPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    contact_name: '',
    phone: '',
    email: '',
    address: '',
    tax_id: '',
  });
  
  const [errors, setErrors] = useState({
    name: '',
    email: '',
    general: ''
  });

  const validate = () => {
    const newErrors = {
      name: '',
      email: '',
      general: ''
    };
    let isValid = true;

    // Validación del nombre (requerido)
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre del proveedor es obligatorio.';
      isValid = false;
    }

    // Validación del email (formato válido si está presente)
    if (formData.email && !/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Por favor, introduce un email válido.';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    
    // Limpiar error específico al editar un campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validar el formulario
    if (!validate()) {
      // No continuar si hay errores
      return;
    }

    setIsSubmitting(true);
    setErrors({ name: '', email: '', general: '' });

    try {
      const response = await createSupplier(formData);
      
      if (response.success) {
        toast.success('Proveedor creado correctamente');
        router.push('/suppliers'); // Redirigir a la lista de proveedores
      } else {
        // Manejar errores de respuesta exitosa pero con error en los datos
        setErrors({ ...errors, general: response.message || 'Error al crear el proveedor' });
        toast.error('Error al crear el proveedor');
      }
    } catch (error) {
      console.error('Error creating supplier:', error);
      
      // Manejar diferentes tipos de errores
      if (error.message.includes('duplicate') || error.message.includes('already exists')) {
        // Error de duplicado (por ejemplo, nombre o email ya existente)
        setErrors({ ...errors, general: 'Este proveedor ya existe en el sistema' });
      } else {
        // Otro tipo de error
        setErrors({ ...errors, general: error.message || 'Error al conectar con el servidor' });
      }
      
      toast.error('No se pudo crear el proveedor');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Crear Nuevo Proveedor</h1>
        <Link href="/suppliers" passHref>
          <button type="button" className="btn btn-secondary">
            <i className="bi bi-arrow-left me-2"></i>Volver a la lista
          </button>
        </Link>
      </div>

      <div className="card shadow-sm">
        <div className="card-body">
          {errors.general && (
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {errors.general}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="nameInput" className="form-label">
                Nombre del Proveedor <span className="text-danger">*</span>
              </label>
              <input 
                type="text" 
                className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                id="nameInput" 
                name="name" 
                value={formData.name} 
                onChange={handleChange} 
                required 
                maxLength="255"
                placeholder="Ingrese el nombre del proveedor" 
              />
              {errors.name && <div className="invalid-feedback">{errors.name}</div>}
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label htmlFor="contactNameInput" className="form-label">Nombre de Contacto</label>
                <input 
                  type="text" 
                  className="form-control" 
                  id="contactNameInput" 
                  name="contact_name" 
                  value={formData.contact_name} 
                  onChange={handleChange} 
                  maxLength="255"
                  placeholder="Persona de contacto" 
                />
              </div>
              <div className="col-md-6">
                <label htmlFor="phoneInput" className="form-label">Teléfono</label>
                <input 
                  type="tel" 
                  className="form-control" 
                  id="phoneInput" 
                  name="phone" 
                  value={formData.phone} 
                  onChange={handleChange} 
                  maxLength="50"
                  placeholder="Número de teléfono" 
                />
              </div>
            </div>

            <div className="row g-3 mb-3">
              <div className="col-md-6">
                <label htmlFor="emailInput" className="form-label">Email</label>
                <input 
                  type="email" 
                  className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                  id="emailInput" 
                  name="email" 
                  value={formData.email} 
                  onChange={handleChange} 
                  maxLength="100"
                  placeholder="correo@ejemplo.com" 
                />
                {errors.email && <div className="invalid-feedback">{errors.email}</div>}
              </div>
              <div className="col-md-6">
                <label htmlFor="taxIdInput" className="form-label">RFC / Tax ID</label>
                <input 
                  type="text" 
                  className="form-control" 
                  id="taxIdInput" 
                  name="tax_id" 
                  value={formData.tax_id} 
                  onChange={handleChange} 
                  maxLength="50"
                  placeholder="Identificación fiscal" 
                />
              </div>
            </div>

            <div className="mb-4">
              <label htmlFor="addressTextarea" className="form-label">Dirección</label>
              <textarea 
                className="form-control" 
                id="addressTextarea" 
                rows="3" 
                name="address" 
                value={formData.address} 
                onChange={handleChange}
                placeholder="Dirección completa del proveedor"
              ></textarea>
            </div>

            <div className="d-flex gap-2">
              <button 
                type="submit" 
                className="btn btn-primary" 
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Guardando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-save me-2"></i>
                    Guardar Proveedor
                  </>
                )}
              </button>
              <Link href="/suppliers" passHref>
                <button type="button" className="btn btn-outline-secondary">
                  Cancelar
                </button>
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}