"use client";

import Link from "next/link";
import {
  getProducts,
  exampleCategories,
  exampleSuppliers,
} from "../../../lib/product-data";
import classNames from "classnames";

export default function ProductListPage() {
  const products = getProducts(); // Obtiene datos de ejemplo

  // Funciones auxiliares para obtener nombres (simulación de JOIN)
  const getCategoryName = (categoryId) => {
    const category = exampleCategories.find(
      (cat) => cat.category_id === categoryId
    );
    return category ? category.name : "Desconocida";
  };
  const getSupplierName = (supplierId) => {
    const supplier = exampleSuppliers.find(
      (sup) => sup.supplier_id === supplierId
    );
    return supplier ? supplier.name : "Desconocido";
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Lista de Productos</h1>
        <Link href="/products/create" passHref>
          <button className="btn btn-primary">Crear Nuevo Producto</button>
        </Link>
      </div>

      {/* Aquí iría la barra de búsqueda/filtrado si la implementas */}

      <table className="table table-striped table-bordered table-hover table-responsive">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Proveedor</th>
            <th>Precio Unitario</th>
            <th>Stock (Total Ejemplo)</th>
            <th>Activo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.product_id}>
              <td>{product.sku}</td>
              <td>{product.name}</td>
              <td>{getCategoryName(product.category_id)}</td>
              <td>{getSupplierName(product.supplier_id)}</td>
              <td>${product.unit_price.toFixed(2)}</td>
              <td>N/A</td>
              <td>{product.is_active ? "Sí" : "No"}</td>
              <td>
                <Link
                  href={`/products/${product.product_id}`}
                  className="btn btn-info btn-sm me-2"
                >
                  Ver
                </Link>
                <Link
                  href={`/products/${product.product_id}/edit`}
                  className="btn btn-warning btn-sm me-2"
                >
                  Editar
                </Link>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => alert(`Eliminar producto ${product.name}`)}
                >
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
