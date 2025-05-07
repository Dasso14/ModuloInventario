// app/reports/stock-levels/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStockLevels, getProductName, getLocationName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function StockLevelsReportPage() {
  const [stockLevels, setStockLevels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carga de datos
    const data = getStockLevels();
    setStockLevels(data);
    setLoading(false);
    // En un sistema real: fetch('/api/reports/stock-levels').then(...)
  }, []);

  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Reporte de Niveles de Stock</h1>
         <Link href="/" passHref >
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

      {/* Aquí irían los filtros (Producto, Ubicación, Categoría, etc.) */}
       <div className="card mb-3">
           <div className="card-body">
               <h6 className="card-title">Filtros (Próximamente)</h6>
               {/* Placeholder para formulario de filtros */}
               <form className="row g-3">
                   <div className="col-md-4">
                       <label htmlFor="filterProduct" className="form-label">Producto</label>
                       <input type="text" className="form-control form-control-sm" id="filterProduct" placeholder="Filtrar por producto" disabled />
                   </div>
                    <div className="col-md-4">
                       <label htmlFor="filterLocation" className="form-label">Ubicación</label>
                       <input type="text" className="form-control form-control-sm" id="filterLocation" placeholder="Filtrar por ubicación" disabled />
                   </div>
                    <div className="col-md-2">
                       <button type="submit" className="btn btn-primary btn-sm mt-4" disabled>Aplicar Filtros</button>
                   </div>
               </form>
           </div>
       </div>


      {stockLevels.length === 0 ? (
           <div className="alert alert-info">No hay niveles de stock registrados.</div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm"> {/* table-sm para tabla más compacta */}
                  <thead>
                    <tr>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad</th>
                      <th>Última Actualización (Simulado)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stockLevels.map(item => (
                      <tr key={item.stock_id}>
                        <td>{getProductName(item.product_id)}</td> {/* Usar función de ayuda */}
                        <td>{getLocationName(item.location_id)}</td> {/* Usar función de ayuda */}
                        <td>{item.quantity}</td>
                        <td>{item.last_updated ? new Date(item.last_updated).toLocaleString() : 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}