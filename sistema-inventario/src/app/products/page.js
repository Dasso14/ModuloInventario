import { useState } from 'react';
import { Button, Table, Form, Modal } from 'react-bootstrap';

export default function Products() {
  const [showModal, setShowModal] = useState(false);
  
  const sampleData = [{
    product_id: 1,
    sku: 'PROD-001',
    name: 'Laptop Gamer',
    unit_price: 1500,
    unit_cost: 1200,
    unit_measure: 'unidad',
    min_stock: 5
  }];

  return (
    <div className="container mt-4">
      <h1>Gestión de Productos</h1>
      <Button variant="primary" onClick={() => setShowModal(true)}>
        Nuevo Producto
      </Button>

      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Nombre</th>
            <th>Precio</th>
            <th>Costo</th>
            <th>Stock Mínimo</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sampleData.map(prod => (
            <tr key={prod.product_id}>
              <td>{prod.sku}</td>
              <td>{prod.name}</td>
              <td>${prod.unit_price}</td>
              <td>${prod.unit_cost}</td>
              <td>{prod.min_stock}</td>
              <td>
                <Button variant="warning" size="sm" className="me-2">Editar</Button>
                <Button variant="danger" size="sm">Eliminar</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Nuevo Producto</Modal.Title>
        </Modal.Header>
        <Form>
          <Modal.Body>
            <div className="row">
              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label>SKU</Form.Label>
                  <Form.Control type="text" required />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Nombre</Form.Label>
                  <Form.Control type="text" required />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Unidad de Medida</Form.Label>
                  <Form.Select>
                    <option value="unidad">Unidad</option>
                    <option value="litro">Litro</option>
                    <option value="kilogramo">Kilogramo</option>
                  </Form.Select>
                </Form.Group>
              </div>

              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label>Precio Unitario</Form.Label>
                  <Form.Control type="number" step="0.01" />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Costo Unitario</Form.Label>
                  <Form.Control type="number" step="0.01" />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Stock Mínimo</Form.Label>
                  <Form.Control type="number" />
                </Form.Group>
              </div>
            </div>

            <Form.Group className="mb-3">
              <Form.Label>Descripción</Form.Label>
              <Form.Control as="textarea" rows={3} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              Guardar
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
}