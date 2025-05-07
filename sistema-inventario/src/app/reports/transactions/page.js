// app/reports/transactions/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getInventoryTransactions, getProductName, getLocationName, getUserName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario
import { useSearchParams } from 'next/navigation'; // Para leer parámetros de URL

export default function TransactionHistoryReportPage() {
  const searchParams = useSearchParams();
  const initialProductId = searchParams.get('productId'); // Leer filtro desde URL

  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
    // Estado para los filtros del formulario (si los implementas)
    // const [filterFormData, setFilterFormData] = useState({
    //     productId: initialProductId || '',
    //     locationId: '',
    //     type: '',
    //     startDate: '',
    //     endDate: '',
    // });

  useEffect(() => {
    setLoading(true);
    // Simular carga de datos con filtro inicial (si viene en la URL)
    const data = getInventoryTransactions({ productId: initialProductId }); // Pasa el filtro a la función mock
    setTransactions(data);
    setLoading(false);

    // En un sistema real, harías un fetch con parámetros de consulta:
    // fetch(`/api/reports/transactions?productId=${initialProductId || ''}&...`)
    // .then(res => res.json())
    // .then(data => { setTransactions(data); setLoading(false); });

  }, [initialProductId]); // Recargar si cambia el filtro de producto en la URL

    // Función para aplicar filtros desde el formulario (si lo implementas)
    // const handleFilterSubmit = (e) => {
    //     e.preventDefault();
    //     // Construir string de query params y navegar
    //     const params = new URLSearchParams();
    //     if (filterFormData.productId) params.set('productId', filterFormData.productId);
    //     // ... añadir otros filtros a params
    //     router.push(`/reports/transactions?${params.toString()}`);
    // };


  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Historial de Transacciones de Inventario</h1>
         <Link href="/" passHref >
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       {/* Aquí irían los filtros avanzados */}
        <div className="card mb-3">
            <div className="card-body">
                <h6 className="card-title">Filtros (Próximamente)</h6>
                <form className="row g-3">
                   <div className="col-md-3">
                       <label htmlFor="filterProduct" className="form-label">Producto</label>
                       <input type="text" className="form-control form-control-sm" id="filterProduct" placeholder="Filtrar por producto" defaultValue={initialProductId} disabled />
                   </div>
                    <div className="col-md-3">
                       <label htmlFor="filterLocation" className="form-label">Ubicación</label>
                       <input type="text" className="form-control form-control-sm" id="filterLocation" placeholder="Filtrar por ubicación" disabled />
                   </div>
                    <div className="col-md-2">
                       <label htmlFor="filterType" className="form-label">Tipo</label>
                       <select className="form-select form-select-sm" id="filterType" disabled>
                           <option value="">Todos</option>
                           <option value="entrada">Entrada</option>
                           <option value="salida">Salida</option>
                           <option value="ajuste">Ajuste</option>
                       </select>
                   </div>
                     <div className="col-md-2">
                       <label htmlFor="filterStartDate" className="form-label">Fecha Desde</label>
                       <input type="date" className="form-control form-control-sm" id="filterStartDate" disabled />
                   </div>
                    <div className="col-md-2">
                       <label htmlFor="filterEndDate" className="form-label">Fecha Hasta</label>
                       <input type="date" className="form-control form-control-sm" id="filterEndDate" disabled />
                   </div>
                    <div className="col-md-2">
                       <button type="submit" className="btn btn-primary btn-sm mt-4" disabled>Aplicar Filtros</button>
                   </div>
               </form>
            </div>
        </div>


      {transactions.length === 0 ? (
           <div className="alert alert-info">No hay transacciones registradas.</div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Tipo</th>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad</th>
                      <th>Referencia</th>
                      <th>Usuario</th>
                      <th>Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(tx => (
                      <tr key={tx.transaction_id}>
                        <td>{new Date(tx.transaction_date).toLocaleString()}</td>
                         <td>
                            
                             <span className={`badge ${tx.transaction_type === 'entrada' ? 'bg-success' : tx.transaction_type === 'salida' ? 'bg-danger' : 'bg-secondary'}`}>
                                 {tx.transaction_type}
                            </span>
                        </td>
                        <td>{getProductName(tx.product_id)}</td>
                        <td>{getLocationName(tx.location_id)}</td>
                        <td>{tx.quantity}</td>
                        <td>{tx.reference_number || 'N/A'}</td>
                        <td>{getUserName(tx.user_id)}</td>
                        <td>{tx.notes || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}