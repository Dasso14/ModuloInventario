"use client"; // Marca como Client Component si usas hooks o interactividad, aunque para un dashboard simple podría ser Server Component

import Link from "next/link"; // Aunque sea Server Component, Link es útil

export default function Dashboard() {
  // Datos de ejemplo para mostrar en el dashboard
  const totalProductos = 150;
  const stockTotal = 5500; // Ejemplo: Suma de todas las cantidades en stock_levels
  const valorInventarioEstimado = 125750.5; // Ejemplo: Resultado de get_inventory_value()
  const productosBajoStock = [
    // Ejemplo: Datos de la vista low_stock
    {
      id: 1,
      sku: "PROD001",
      name: "Laptop ABC",
      location: "Almacén Principal",
      quantity: 5,
      min_stock: 10,
    },
    {
      id: 7,
      sku: "PROD007",
      name: "Mouse Óptico XYZ",
      location: "Tienda 1",
      quantity: 12,
      min_stock: 15,
    },
    // ... más productos bajo stock
  ];
  const transaccionesRecientes = [
    // Ejemplo: Datos de inventory_transactions
    {
      id: 101,
      date: "2025-05-06",
      type: "entrada",
      product: "Laptop ABC",
      quantity: 20,
      location: "Almacén Principal",
    },
    {
      id: 102,
      date: "2025-05-06",
      type: "salida",
      product: "Mouse Óptico XYZ",
      quantity: 5,
      location: "Tienda 1",
    },
    {
      id: 103,
      date: "2025-05-05",
      type: "ajuste",
      product: "Cable USB",
      quantity: -2,
      location: "Almacén Principal",
    },
  ];

  return (
    <>
      <h1>Dashboard del Inventario</h1>

      {/* Fila con 3 tarjetas */}
      <div className="row mt-4">
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Total Productos</h5>
              <div className="card-text">
                {" "}
                {/* Changed p to div */}
                <h2>{totalProductos}</h2>
                <Link href="/products" className="btn btn-primary">
                  Ver Productos
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Stock Total Estimado</h5>
              <div className="card-text">
                {" "}
                {/* Changed p to div */}
                <h2>{stockTotal}</h2>
                <Link href="/reports/stock-levels" className="btn btn-primary">
                  Ver Niveles de Stock
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h5 className="card-title">Valor Total Inventario</h5>
              <div className="card-text">
                {" "}
                {/* Changed p to div */}
                <h2>${valorInventarioEstimado.toFixed(2)}</h2>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Fila con 2 tarjetas */}
      <div className="row mt-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Productos con Stock Bajo</h5>
              <ul className="list-group list-group-flush">
                {productosBajoStock.length > 0 ? (
                  productosBajoStock.map((item) => (
                    <li key={item.id} className="list-group-item">
                      <Link href={`/products/${item.id}`}>
                        {item.sku} - {item.name}
                      </Link>{" "}
                      en {item.location}: {item.quantity} (Min: {item.min_stock}
                      )
                    </li>
                  ))
                ) : (
                  <li className="list-group-item">
                    No hay productos con stock bajo.
                  </li>
                )}
              </ul>
              <div className="mt-2">
                <Link href="/reports/low-stock" className="btn btn-link">
                  Ver Reporte Completo
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Transacciones Recientes</h5>
              <ul className="list-group list-group-flush">
                {transaccionesRecientes.length > 0 ? (
                  transaccionesRecientes.map((tx) => (
                    <li key={tx.id} className="list-group-item">
                      <Link href={`/reports/transactions?id=${tx.id}`}>
                        [{tx.date}]{" "}
                        <span
                          className={`badge ${
                            tx.type === "entrada"
                              ? "bg-success"
                              : tx.type === "salida"
                              ? "bg-danger"
                              : "bg-secondary"
                          }`}
                        >
                          {tx.type}
                        </span>{" "}
                        {tx.product}: {tx.quantity} en {tx.location}
                      </Link>
                    </li>
                  ))
                ) : (
                  <li className="list-group-item">
                    No hay transacciones recientes.
                  </li>
                )}
              </ul>
              <div className="mt-2">
                <Link href="/reports/transactions" className="btn btn-link">
                  Ver Historial Completo
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
