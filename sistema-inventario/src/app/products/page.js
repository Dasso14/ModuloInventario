// app/products/page.js
"use client";

import { Container, Table, Button } from 'react-bootstrap';
import Link from 'next/link';
import { getProducts, exampleCategories, exampleSuppliers } from '@/lib/product-data'; // Ajusta la ruta si es necesario

export default function ProductListPage() {
  const products = getProducts(); // Obtiene datos de ejemplo

  // Funciones auxiliares para obtener nombres (simulación de JOIN)
  const getCategoryName = (categoryId) => {
      const category = exampleCategories.find(cat => cat.category_id === categoryId);
      return category ? category.name : 'Desconocida';
  };
   const getSupplierName = (supplierId) => {
      const supplier = exampleSuppliers.find(sup => sup.supplier_id === supplierId);
      return supplier ? supplier.name : 'Desconocido';
  };


  return (
    <> {/* El Container principal viene del layout */}
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Lista de Productos</h1>
        <Link href="/products/create" passHref legacyBehavior> {/* Usamos legacyBehavior con as=Button si queremos que Link renderice el Button */}
           <Button variant="primary">Crear Nuevo Producto</Button>
        </Link>
      </div>

      {/* Aquí iría la barra de búsqueda/filtrado si la implementas */}

      <Table striped bordered hover responsive>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Proveedor</th>
            <th>Precio Unitario</th>
            <th>Stock (Total Ejemplo)</th>{/* Nota: Stock real requiere unir con stock_levels y sumar */}
            <th>Activo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.product_id}>
              <td>{product.sku}</td>
              <td>{product.name}</td>
              <td>{getCategoryName(product.category_id)}</td> {/* Usando función auxiliar */}
              <td>{getSupplierName(product.supplier_id)}</td> {/* Usando función auxiliar */}
              <td>${product.unit_price.toFixed(2)}</td>
              <td>{/* Stock real aquí - SIMULADO */} N/A</td>{/* En un sistema real, buscarías el stock total o por ubicación */}
              <td>{product.is_active ? 'Sí' : 'No'}</td>
              <td>
                <Link href={`/products/${product.product_id}`} passHref legacyBehavior>
                  <Button variant="info" size="sm" className="me-2">Ver</Button>
                </Link>
                 <Link href={`/products/${product.product_id}/edit`} passHref legacyBehavior>
                  <Button variant="warning" size="sm" className="me-2">Editar</Button>
                </Link>
                 <Button variant="danger" size="sm" onClick={() => alert(`Eliminar producto ${product.name}`)}>Eliminar</Button> {/* Implementar lógica real */}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
}