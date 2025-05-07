// app/products/[id]/edit/page.js
"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Container, Form, Button, Card, Row, Col, Spinner, Alert } from 'react-bootstrap';
import Link from 'next/link';
import { getProductById, exampleCategories, exampleSuppliers } from '../../../../../lib/product-data'; // Ajusta la ruta si es necesario

export default function EditProductPage() {
  const router = useRouter();
  const params = useParams();
  const productId = params.id ? parseInt(params.id, 10) : null;

  const [product, setProduct] = useState(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category_id: '',
    supplier_id: '',
    unit_cost: '',
    unit_price: '',
    unit_measure: 'unidad',
    weight: '',
    volume: '',
    min_stock: '0',
    max_stock: '',
    is_active: true,
  });

  useEffect(() => {
    if (productId !== null && !isNaN(productId)) {
      setLoading(true);
      setError(null);
      const foundProduct = getProductById(productId);

      if (foundProduct) {
        setProduct(foundProduct);
        setFormData({
          sku: foundProduct.sku,
          name: foundProduct.name,
          description: foundProduct.description || '',
          category_id: foundProduct.category_id.toString(),
          supplier_id: foundProduct.supplier_id.toString(),
          unit_cost: foundProduct.unit_cost.toString(),
          unit_price: foundProduct.unit_price.toString(),
          unit_measure: foundProduct.unit_measure,
          weight: foundProduct.weight !== null ? foundProduct.weight.toString() : '',
          volume: foundProduct.volume !== null ? foundProduct.volume.toString() : '',
          min_stock: foundProduct.min_stock.toString(),
          max_stock: foundProduct.max_stock !== null ? foundProduct.max_stock.toString() : '',
          is_active: foundProduct.is_active,
        });
        setLoading(false);
      } else {
        setError(`Producto con ID ${productId} no encontrado.`);
        setLoading(false);
      }
    } else {
      setError("ID de producto inválido en la URL.");
      setLoading(false);
    }
  }, [productId]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Datos a actualizar:', formData);
    alert(`Producto ${product?.name} actualizado (simulado)`);
    router.push(`/products/${productId}`);
  };

  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (!product) {
    return <Alert variant="warning">Producto no disponible.</Alert>;
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Editar Producto: {product.name}</h1>
        <Link href={`/products/${product.product_id}`} passHref >
          <Button variant="secondary">Cancelar</Button>
        </Link>
      </div>

      <Card>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row className="mb-3">
              <Form.Group as={Col} controlId="formSku">
                <Form.Label>SKU</Form.Label>
                <Form.Control type="text" name="sku" value={formData.sku} onChange={handleChange} required />
              </Form.Group>
              <Form.Group as={Col} controlId="formName">
                <Form.Label>Nombre</Form.Label>
                <Form.Control type="text" name="name" value={formData.name} onChange={handleChange} required />
              </Form.Group>
            </Row>

            <Form.Group className="mb-3" controlId="formDescription">
              <Form.Label>Descripción</Form.Label>
              <Form.Control as="textarea" rows={3} name="description" value={formData.description} onChange={handleChange} />
            </Form.Group>

            <Row className="mb-3">
              <Form.Group as={Col} controlId="formCategory">
                <Form.Label>Categoría</Form.Label>
                <Form.Select name="category_id" value={formData.category_id} onChange={handleChange} required>
                  <option value="">Seleccione una categoría</option>
                  {exampleCategories.map(category => (
                    <option key={category.category_id} value={category.category_id}>{category.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group as={Col} controlId="formSupplier">
                <Form.Label>Proveedor</Form.Label>
                <Form.Select name="supplier_id" value={formData.supplier_id} onChange={handleChange} required>
                  <option value="">Seleccione un proveedor</option>
                  {exampleSuppliers.map(supplier => (
                    <option key={supplier.supplier_id} value={supplier.supplier_id}>{supplier.name}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} controlId="formUnitCost">
                <Form.Label>Costo Unitario</Form.Label>
                <Form.Control type="number" step="0.01" name="unit_cost" value={formData.unit_cost} onChange={handleChange} required />
              </Form.Group>
              <Form.Group as={Col} controlId="formUnitPrice">
                <Form.Label>Precio Unitario</Form.Label>
                <Form.Control type="number" step="0.01" name="unit_price" value={formData.unit_price} onChange={handleChange} required />
              </Form.Group>
              <Form.Group as={Col} controlId="formUnitMeasure">
                <Form.Label>Unidad de Medida</Form.Label>
                <Form.Select name="unit_measure" value={formData.unit_measure} onChange={handleChange} required>
                  <option value="unidad">Unidad</option>
                  <option value="litro">Litro</option>
                  <option value="kilogramo">Kilogramo</option>
                  <option value="metro">Metro</option>
                  <option value="caja">Caja</option>
                </Form.Select>
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} controlId="formWeight">
                <Form.Label>Peso (kg)</Form.Label>
                <Form.Control type="number" step="0.01" name="weight" value={formData.weight} onChange={handleChange} />
              </Form.Group>
              <Form.Group as={Col} controlId="formVolume">
                <Form.Label>Volumen (m³)</Form.Label>
                <Form.Control type="number" step="0.01" name="volume" value={formData.volume} onChange={handleChange} />
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} controlId="formMinStock">
                <Form.Label>Stock Mínimo</Form.Label>
                <Form.Control type="number" name="min_stock" value={formData.min_stock} onChange={handleChange} required />
              </Form.Group>
              <Form.Group as={Col} controlId="formMaxStock">
                <Form.Label>Stock Máximo</Form.Label>
                <Form.Control type="number" name="max_stock" value={formData.max_stock} onChange={handleChange} />
              </Form.Group>
            </Row>

            <Form.Group className="mb-3" controlId="formIsActive">
              <Form.Check
                type="checkbox"
                label="Producto Activo"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
              />
            </Form.Group>

            <Button variant="primary" type="submit">
              Actualizar Producto
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </>
  );
}
