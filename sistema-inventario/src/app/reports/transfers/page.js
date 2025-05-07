// app/reports/transfers/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getLocationTransfers, getProductName, getLocationName, getUserName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function LocationTransfersReportPage() {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simular carga de datos
    const data = getLocationTransfers();
    setTransfers(data);
    setLoading(false);
    // En un sistema real: fetch('/api/reports/transfers').then(...)
  }, []);

  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Reporte de Transferencias entre Ubicaciones</h1>
         <Link href="/" passHref >
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       {/* Aquí irían los filtros */}
       {/* ... Placeholder de filtros ... */}


      {transfers.length === 0 ? (
           <div className="alert alert-info">No hay transferencias registradas.</div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Producto</th>
                      <th>Origen</th>
                      <th>Destino</th>
                      <th>Cantidad</th>
                      <th>Usuario</th>
                      <th>Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transfers.map(transfer => (
                      <tr key={transfer.transfer_id}>
                        <td>{new Date(transfer.transfer_date).toLocaleString()}</td>
                        <td>{getProductName(transfer.product_id)}</td>
                        <td>{getLocationName(transfer.from_location_id)}</td>
                        <td>{getLocationName(transfer.to_location_id)}</td>
                        <td>{transfer.quantity}</td>
                        <td>{getUserName(transfer.user_id)}</td>
                        <td>{transfer.notes || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}