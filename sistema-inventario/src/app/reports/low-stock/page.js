// app/reports/low-stock/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getProducts, getStockLevels, getProductName, getLocationName } from '../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function LowStockReportPage() {
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // Simular procesamiento de datos para encontrar stock bajo
    const products = getProducts();
    const stockLevels = getStockLevels();

    const lowStock = [];
    stockLevels.forEach(sl => {
        const product = products.find(p => p.product_id === sl.product_id);
        if (product && sl.quantity <= product.min_stock) {
            lowStock.push({
                stock_id: sl.stock_id, // Usar ID único si es posible, o una combinación
                product_id: product.product_id,
                sku: product.sku,
                product_name: product.name,
                location_id: sl.location_id,
                location_name: getLocationName(sl.location_id),
                quantity: sl.quantity,
                min_stock: product.min_stock
            });
        }
    });

    setLowStockItems(lowStock);
    setLoading(false);

    // En un sistema real, usarías la vista low_stock de la base de datos:
    // fetch('/api/reports/low-stock').then(...)
  }, []);

  if (loading) {
    return <div className="text-center">Cargando...</div>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Reporte de Productos con Stock Bajo</h1>
         <Link href="/" passHref legacyBehavior>
            <button type="button" className="btn btn-secondary">Volver al Dashboard</button>
        </Link>
      </div>

       {/* Aquí irían los filtros */}
       {/* ... Placeholder de filtros ... */}


      {lowStockItems.length === 0 ? (
           <div className="alert alert-success">No hay productos con stock bajo. ¡Inventario saludable!</div>
      ) : (
           <div className="table-responsive">
                <table className="table table-striped table-bordered table-hover table-sm">
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Producto</th>
                      <th>Ubicación</th>
                      <th>Cantidad Actual</th>
                      <th>Stock Mínimo</th>
                      <th>Acciones</th> {/* Enlace a detalles del producto/stock */}
                    </tr>
                  </thead>
                  <tbody>
                    {lowStockItems.map((item, index) => (
                      <tr key={item.stock_id || index}> {/* Usar stock_id si es único, o index como fallback */}
                        <td>{item.sku}</td>
                        <td>{item.product_name}</td>
                        <td>{item.location_name}</td>
                        <td>{item.quantity}</td>
                        <td>{item.min_stock}</td>
                         <td>
                             <Link href={`/products/${item.product_id}`} passHref legacyBehavior>
                                 <button type="button" className="btn btn-info btn-sm">Ver Producto</button>
                             </Link>
                             {/* Podrías añadir un enlace a la pantalla de agregar stock para esta ubicación/producto */}
                         </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
      )}
    </>
  );
}