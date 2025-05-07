import { Inter } from "next/font/google";
import Link from "next/link";
import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Sistema de Inventario",
  description: "Gestión de inventario con Next.js",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <head>
        {/* Asegura que el JS de Bootstrap esté cargado para habilitar dropdowns y collapses */}
        <script
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
          defer
        ></script>
      </head>
      <body className={`${inter.className} bg-light`}>
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
          <div className="container">
            <Link href="/" className="navbar-brand">
              Inventario
            </Link>
            <button
              className="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#main-navbar"
              aria-controls="main-navbar"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>

            <div className="collapse navbar-collapse" id="main-navbar">
              <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                {/* Enlace directo para móviles */}
                <li className="nav-item d-lg-none">
                  <Link href="/products" className="nav-link">Productos</Link>
                </li>

                {/* Maestros */}
                <li className="nav-item dropdown">
                  <a
                    className="nav-link dropdown-toggle"
                    href="#"
                    id="maestrosDropdown"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    Maestros
                  </a>
                  <ul className="dropdown-menu" aria-labelledby="maestrosDropdown">
                    <li><Link href="/products" className="dropdown-item">Productos</Link></li>
                    <li><Link href="/categories" className="dropdown-item">Categorías</Link></li>
                    <li><Link href="/suppliers" className="dropdown-item">Proveedores</Link></li>
                    <li><Link href="/locations" className="dropdown-item">Ubicaciones</Link></li>
                  </ul>
                </li>

                {/* Operaciones */}
                <li className="nav-item dropdown">
                  <a
                    className="nav-link dropdown-toggle"
                    href="#"
                    id="operacionesDropdown"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    Operaciones
                  </a>
                  <ul className="dropdown-menu" aria-labelledby="operacionesDropdown">
                    <li><Link href="/inventory/add" className="dropdown-item">Registrar Entrada</Link></li>
                    <li><Link href="/inventory/remove" className="dropdown-item">Registrar Salida</Link></li>
                    <li><Link href="/inventory/adjust" className="dropdown-item">Ajuste de Stock</Link></li>
                    <li><hr className="dropdown-divider" /></li>
                    <li><Link href="/inventory/transfer" className="dropdown-item">Transferir Stock</Link></li>
                  </ul>
                </li>

                {/* Reportes */}
                <li className="nav-item dropdown">
                  <a
                    className="nav-link dropdown-toggle"
                    href="#"
                    id="reportesDropdown"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                  >
                    Reportes
                  </a>
                  <ul className="dropdown-menu" aria-labelledby="reportesDropdown">
                    <li><Link href="/reports/stock-levels" className="dropdown-item">Niveles de Stock</Link></li>
                    <li><Link href="/reports/transactions" className="dropdown-item">Historial de Transacciones</Link></li>
                    <li><Link href="/reports/low-stock" className="dropdown-item">Stock Bajo</Link></li>
                    <li><Link href="/reports/transfers" className="dropdown-item">Historial de Transferencias</Link></li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        <main className="container mt-4">
          {children}
        </main>
      </body>
    </html>
  );
}
