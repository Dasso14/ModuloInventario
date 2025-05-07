// app/products/[id]/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Container, Card, Button, Row, Col, Table } from 'react-bootstrap';
import Link from 'next/link';
import { getProductById, getStockLevelsByProductId, exampleCategories, exampleSuppliers } from '@/lib/product-data';

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
    if (categoryId === undefined) return 'N/A';
    const category = exampleCategories.find(cat => cat.category_id === categoryId);
    return category ? category.name : 'Desconocida';
  };

  const getSupplierName = (supplierId) => {
    if (supplierId === undefined) return 'N/A';
    const supplier = exampleSuppliers.find(sup => sup.supplier_id === supplierId);
    return supplier ? supplier.name : 'Desconocido';
  };

  const getLocationName = (locationId) => {
    const exampleLocations = [
      { location_id: 1, name: 'Almacén Principal' },
      { location_id: 2, name: 'Tienda 1' }
    ];
    const location = exampleLocations.find(loc => loc.location_id === locationId);
    return location ? location.name : 'Desconocida';
  };

  if (productId === null || isNaN(productId)) {
    return <>Producto no encontrado o ID inválido.</>;
  }

  if (!product) {
    return <>Cargando...</>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Detalles del Producto: {product.name}</h1>
        <div>
          <Link href={`/products/${product.product_id}/edit`} passHref legacyBehavior>
            <Button variant="warning" className="me-2">Editar</Button>
          </Link>
          <Link href="/products" passHref legacyBehavior>
            <Button variant="secondary">Volver a la Lista</Button>
          </Link>
        </div>
      </div>

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Información General</Card.Title>
          <Row>
            <Col md={6}>
              <p><strong>SKU:</strong> {product.sku}</p>
              <p><strong>Nombre:</strong> {product.name}</p>
              <p><strong>Descripción:</strong> {product.description || 'N/A'}</p>
              <p><strong>Categoría:</strong> {getCategoryName(product.category_id)}</p>
              <p><strong>Proveedor:</strong> {getSupplierName(product.supplier_id)}</p>
            </Col>
            <Col md={6}>
              <p><strong>Costo Unitario:</strong> ${product.unit_cost.toFixed(2)}</p>
              <p><strong>Precio Unitario:</strong> ${product.unit_price.toFixed(2)}</p>
              <p><strong>Unidad de Medida:</strong> {product.unit_measure}</p>
              <p><strong>Peso:</strong> {product.weight !== null ? `${product.weight} kg` : 'N/A'}</p>
              <p><strong>Volumen:</strong> {product.volume !== null ? `${product.volume} m³` : 'N/A'}</p>
            </Col>
          </Row>
          <Row className="mt-3">
            <Col>
              <p><strong>Stock Mínimo:</strong> {product.min_stock}</p>
              <p><strong>Stock Máximo:</strong> {product.max_stock !== null ? product.max_stock : 'N/A'}</p>
              <p><strong>Estado:</strong> {product.is_active ? 'Activo' : 'Inactivo'}</p>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Niveles de Stock por Ubicación</Card.Title>
          {stockLevels.length > 0 ? (
            <Table striped bordered hover size="sm">
              <thead>
                <tr>
                  <th>Ubicación</th>
                  <th>Cantidad</th>
                </tr>
              </thead>
              <tbody>
                {stockLevels.map(sl => (
                  <tr key={sl.stock_id}>
                    <td>{getLocationName(sl.location_id)}</td>
                    <td>{sl.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <p>No hay registros de stock para este producto.</p>
          )}
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Códigos de Barras</Card.Title>
          <p>Aquí se listarían y gestionarían los códigos de barras asociados a este producto.</p>
          <Button variant="outline-primary" size="sm">Agregar Código de Barras</Button>
        </Card.Body>
      </Card>

      <Card>
        <Card.Body>
          <Card.Title>Historial de Transacciones</Card.Title>
          <p>Aquí se listarían las transacciones de inventario (`inventory_transactions`) para este producto.</p>
          <Link href={`/reports/transactions?productId=${product.product_id}`}>Ver todas las transacciones de este producto</Link>
        </Card.Body>
      </Card>
    </>
  );
}
