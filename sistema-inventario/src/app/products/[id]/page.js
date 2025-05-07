"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  getProductById,
  getStockLevelsByProductId,
  exampleCategories,
  exampleSuppliers,
} from "../../../../lib/product-data";
import classNames from "classnames";

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params.id ? parseInt(params.id, 10) : null;

  const [product, setProduct] = useState(undefined);
  const [stockLevels, setStockLevels] = useState([]);

  useEffect(() => {
    if (productId !== null && !isNaN(productId)) {
      const foundProduct = getProductById(productId);
      setProduct(foundProduct);

      const relatedStock = getStockLevelsByProductId(productId);
      setStockLevels(relatedStock);
    }
  }, [productId]);

  const getCategoryName = (categoryId) => {
    if (categoryId === undefined) return "N/A";
    const category = exampleCategories.find(
      (cat) => cat.category_id === categoryId
    );
    return category ? category.name : "Desconocida";
  };

  const getSupplierName = (supplierId) => {
    if (supplierId === undefined) return "N/A";
    const supplier = exampleSuppliers.find(
      (sup) => sup.supplier_id === supplierId
    );
    return supplier ? supplier.name : "Desconocido";
  };

  const getLocationName = (locationId) => {
    const exampleLocations = [
      { location_id: 1, name: "Almacén Principal" },
      { location_id: 2, name: "Tienda 1" },
    ];
    const location = exampleLocations.find(
      (loc) => loc.location_id === locationId
    );
    return location ? location.name : "Desconocida";
  };

  if (productId === null || isNaN(productId)) {
    return <>Producto no encontrado o ID inválido.</>;
  }

  if (!product) {
    return <>Cargando...</>;
  }

  return (
    <>
      <div
        className={classNames(
          "d-flex",
          "justify-content-between",
          "align-items-center",
          "mb-3"
        )}
      >
        <h1>Detalles del Producto: {product.name}</h1>
        <div>
          <Link
            href={`/products/${product.product_id}/edit`}
            className="btn btn-warning me-2"
          >
            Editar
          </Link>
          <Link href="/products" className="btn btn-secondary">
            Volver a la Lista
          </Link>
        </div>
      </div>

      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <div className="row">
            <div className="col-md-6">
              <p>
                <strong>SKU:</strong> {product.sku}
              </p>
              <p>
                <strong>Nombre:</strong> {product.name}
              </p>
              <p>
                <strong>Descripción:</strong> {product.description || "N/A"}
              </p>
              <p>
                <strong>Categoría:</strong>{" "}
                {getCategoryName(product.category_id)}
              </p>
              <p>
                <strong>Proveedor:</strong>{" "}
                {getSupplierName(product.supplier_id)}
              </p>
            </div>
            <div className="col-md-6">
              <p>
                <strong>Costo Unitario:</strong> ${product.unit_cost.toFixed(2)}
              </p>
              <p>
                <strong>Precio Unitario:</strong> $
                {product.unit_price.toFixed(2)}
              </p>
              <p>
                <strong>Unidad de Medida:</strong> {product.unit_measure}
              </p>
              <p>
                <strong>Peso:</strong>{" "}
                {product.weight !== null ? `${product.weight} kg` : "N/A"}
              </p>
              <p>
                <strong>Volumen:</strong>{" "}
                {product.volume !== null ? `${product.volume} m³` : "N/A"}
              </p>
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <p>
                <strong>Stock Mínimo:</strong> {product.min_stock}
              </p>
              <p>
                <strong>Stock Máximo:</strong>{" "}
                {product.max_stock !== null ? product.max_stock : "N/A"}
              </p>
              <p>
                <strong>Estado:</strong>{" "}
                {product.is_active ? "Activo" : "Inactivo"}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Niveles de Stock por Ubicación</h5>
          {stockLevels.length > 0 ? (
            <table className="table table-striped table-bordered table-hover table-sm">
              <thead>
                <tr>
                  <th>Ubicación</th>
                  <th>Cantidad</th>
                </tr>
              </thead>
              <tbody>
                {stockLevels.map((sl) => (
                  <tr key={sl.stock_id}>
                    <td>{getLocationName(sl.location_id)}</td>
                    <td>{sl.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No hay registros de stock para este producto.</p>
          )}
        </div>
      </div>

      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Códigos de Barras</h5>
          <p>
            Aquí se listarían y gestionarían los códigos de barras asociados a
            este producto.
          </p>
          <button className="btn btn-outline-primary btn-sm">
            Agregar Código de Barras
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Historial de Transacciones</h5>
          <p>
            Aquí se listarían las transacciones de inventario
            (`inventory_transactions`) para este producto.
          </p>
          <Link href={`/reports/transactions?productId=${product.product_id}`}>
            Ver todas las transacciones de este producto
          </Link>
        </div>
      </div>
    </>
  );
}
