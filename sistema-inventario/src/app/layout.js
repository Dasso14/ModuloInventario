import { Inter } from "next/font/google";
import Link from "next/link"; // Importa Link de next/link
import { Container, Navbar, Nav, NavDropdown } from 'react-bootstrap'; // Importa componentes de react-bootstrap

// Importa Bootstrap CSS
// Asegúrate de que la ruta sea correcta según tu configuración (node_modules)
import 'bootstrap/dist/css/bootstrap.min.css';
import './globals.css'; // Archivo global de CSS si lo tienes

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Sistema de Inventario",
  description: "Gestión de inventario con Next.js y React-Bootstrap",
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body className={inter.className}>
        {/* Barra de Navegación */}
        <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
          <Container>
            <Navbar.Brand as={Link} href="/" passHref> {/* Link a la página principal/Dashboard */}
              Sistema de Inventario
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">

                {/* Dropdown: Maestros */}
                <NavDropdown title="Maestros" id="basic-nav-dropdown-maestros">
                  <NavDropdown.Item as={Link} href="/products" passHref>Productos</NavDropdown.Item>
                  <NavDropdown.Item as={Link} href="/categories" passHref>Categorías</NavDropdown.Item>
                  <NavDropdown.Item as={Link} href="/suppliers" passHref>Proveedores</NavDropdown.Item>
                  <NavDropdown.Item as={Link} href="/locations" passHref>Ubicaciones</NavDropdown.Item>
                </NavDropdown>

                {/* Dropdown: Operaciones de Inventario */}
                <NavDropdown title="Operaciones" id="basic-nav-dropdown-operaciones">
                  <NavDropdown.Item as={Link} href="/inventory/add" passHref>Registrar Entrada</NavDropdown.Item>
                  <NavDropdown.Item as={Link} href="/inventory/remove" passHref>Registrar Salida</NavDropdown.Item>
                  <NavDropdown.Item as={Link} href="/inventory/adjust" passHref>Ajuste de Stock</NavDropdown.Item>
                  <NavDropdown.Divider /> {/* Separador */}
                  <NavDropdown.Item as={Link} href="/inventory/transfer" passHref>Transferir Stock</NavDropdown.Item>
                </NavDropdown>

                {/* Dropdown: Reportes */}
                <NavDropdown title="Reportes" id="basic-nav-dropdown-reportes">
                   <NavDropdown.Item as={Link} href="/reports/stock-levels" passHref>Niveles de Stock</NavDropdown.Item>
                   <NavDropdown.Item as={Link} href="/reports/transactions" passHref>Historial de Transacciones</NavDropdown.Item>
                   <NavDropdown.Item as={Link} href="/reports/low-stock" passHref>Stock Bajo</NavDropdown.Item>
                   <NavDropdown.Item as={Link} href="/reports/transfers" passHref>Historial de Transferencias</NavDropdown.Item>
                </NavDropdown>

              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        {/* Contenido de la página actual */}
        <Container className="mt-4"> {/* Agrega un margen superior para que el contenido no quede debajo de la barra */}
          {children}
        </Container>
      </body>
    </html>
  );
}