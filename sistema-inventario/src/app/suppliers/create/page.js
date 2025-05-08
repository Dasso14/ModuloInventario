// app/suppliers/create/page.js
"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
// Importamos la función del nuevo servicio
import { createSupplier } from '../../../services/supplierService'; // Ajusta la ruta si es necesario

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
     // Limpiar error general si se empieza a escribir de nuevo
     if (errors.general && name !== 'general') {
        setErrors(prev => ({ ...prev, general: '' }));
     }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validar el formulario
    if (!validate()) {
      // No continuar si hay errores
      toast.error('Por favor, corrige los errores en el formulario.'); // Notificar al usuario
      return;
    }

    setIsSubmitting(true);
    setErrors({ name: '', email: '', general: '' }); // Limpiar errores antes de enviar

    try {
      // Usar la función createSupplier del servicio
      const response = await createSupplier(formData);

      // Asumimos que el servicio/API devuelve una respuesta con { success: boolean, ... }
      if (response && response.success) {
        toast.success('Proveedor creado correctamente');
        router.push('/suppliers'); // Redirigir a la lista de proveedores
      } else {
        // Manejar errores de respuesta exitosa pero con error en los datos (ej. validación del backend)
        // O si el servicio devuelve success: false y un message
        const errorMessage = response?.message || 'Error desconocido al crear el proveedor';
        setErrors({ ...errors, general: errorMessage });
        toast.error(errorMessage); // Mostrar el mensaje de error específico de la API si está disponible
      }
    } catch (error) {
      console.error('Error creating supplier:', error);

      // Manejar errores de red o del servicio (como throw new Error)
      // Intentar extraer un mensaje útil del error
      const errorMessage = error.message || 'Error de comunicación con el servidor';

      // Puedes añadir lógica para detectar tipos específicos de errores si tu API los señala en el mensaje
      if (errorMessage.toLowerCase().includes('duplicate') || errorMessage.toLowerCase().includes('already exists')) {
         setErrors({ ...errors, general: 'Ya existe un proveedor con estos datos (nombre/email).' });
         toast.error('Error: Proveedor duplicado.');
      } else {
         setErrors({ ...errors, general: errorMessage });
         toast.error('Error al crear el proveedor.');
      }
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

          <form onSubmit={handleSubmit} noValidate> {/* Añadimos noValidate para confiar en nuestra validación JS */}
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
                disabled={isSubmitting} // Deshabilitar mientras se envía
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
                  disabled={isSubmitting} // Deshabilitar mientras se envía
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
                  disabled={isSubmitting} // Deshabilitar mientras se envía
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
                  disabled={isSubmitting} // Deshabilitar mientras se envía
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
                  disabled={isSubmitting} // Deshabilitar mientras se envía
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
                disabled={isSubmitting} // Deshabilitar mientras se envía
              ></textarea>
            </div>

            <div className="d-flex gap-2">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting} // Deshabilitar si isSubmitting es true
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
                <button type="button" className="btn btn-outline-secondary" disabled={isSubmitting}>
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