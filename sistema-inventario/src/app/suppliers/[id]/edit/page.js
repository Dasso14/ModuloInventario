// app/suppliers/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
// Importamos las funciones del nuevo servicio
import { getSupplierById, updateSupplier } from '../../../../services/supplierService'; // Ajusta la ruta si es necesario

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
    const fetchSupplier = async () => {
      if (supplierId !== null && !isNaN(supplierId)) {
        setLoading(true);
        setError(null);
        try {
          // Usar la función del servicio para obtener el proveedor
          const result = await getSupplierById(supplierId);

          // Asumiendo que el servicio devuelve { success: true, data: {...} }
          if (result && result.success) {
            const foundSupplier = result.data;
            setSupplier(foundSupplier);
            // Precargar el formulario con los datos existentes
            setFormData({
              name: foundSupplier.name || '', // Asegurarse de usar un string vacío para evitar warnings
              contact_name: foundSupplier.contact_name || '',
              phone: foundSupplier.phone || '',
              email: foundSupplier.email || '',
              address: foundSupplier.address || '',
              tax_id: foundSupplier.tax_id || '',
            });
          } else {
            // Manejar caso donde success es false o no se encuentra el proveedor
            setError(result?.message || `Proveedor con ID ${supplierId} no encontrado.`);
          }
        } catch (err) {
          // Manejar errores de red o del servicio
          setError(`Error al cargar proveedor: ${err.message}`);
        } finally {
          setLoading(false);
        }
      } else {
        setError("ID de proveedor inválido en la URL.");
        setLoading(false);
      }
    };

    fetchSupplier();
  }, [supplierId]); // Dependencia: recargar si cambia el ID en la URL


  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
    setFormError(''); // Limpiar error al cambiar algo
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // --- Validación simple ---
    if (!formData.name.trim()) { // Añadir .trim() para evitar nombres solo con espacios
      setFormError('El nombre del proveedor es obligatorio.');
      return;
    }
    // --- Fin Validación simple ---

    setLoading(true); // Mostrar estado de carga mientras se actualiza
    try {
      // Usar la función del servicio para actualizar el proveedor
      const result = await updateSupplier(supplierId, formData);

      // Asumiendo que el servicio devuelve { success: true, data: {...} } o { success: true, message: "..." }
      if (result && result.success) {
        console.log('Proveedor actualizado exitosamente', result.data);
        alert(`Proveedor ${formData.name} actualizado.`); // O usa un sistema de notificaciones mejor
        router.push(`/suppliers/${supplierId}`); // Redirigir a los detalles del proveedor
      } else {
        // Manejar caso donde success es false
        setFormError(result?.message || 'Error al actualizar el proveedor.');
      }
    } catch (err) {
      // Manejar errores de red o del servicio
      setFormError(`Error en la comunicación con el servidor: ${err.message}`);
    } finally {
       setLoading(false); // Ocultar estado de carga
    }
  };

  if (loading) {
    return (
      <div className="text-center p-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-2">{supplier ? 'Guardando cambios...' : 'Cargando datos del proveedor...'}</p> {/* Mensaje más específico */}
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  if (!supplier) {
    // Este caso debería ser cubierto por el error al no encontrar el proveedor,
    // pero lo mantenemos como fallback.
    return <div className="alert alert-warning">Proveedor no disponible.</div>;
  }


  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Editar Proveedor: {supplier.name}</h1>
        <Link href={`/suppliers/${supplierId}`} passHref > {/* Usar supplierId, no supplier.supplier_id si el params.id es el que usas */}
          <button type="button" className="btn btn-secondary">Cancelar</button>
        </Link>
      </div>

      <div className="card">
        <div className="card-body">
          {formError && <div className="alert alert-danger">{formError}</div>}
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

            <button type="submit" className="btn btn-primary" disabled={loading}> {/* Deshabilitar botón mientras carga */}
              {loading ? 'Actualizando...' : 'Actualizar Proveedor'}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}