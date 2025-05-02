import { useState } from 'react';
import { Button, Table, Form, Modal, Badge } from 'react-bootstrap';

export default function InventoryTransactions() {
  const [showModal, setShowModal] = useState(false);
  
  const sampleData = [{
    transaction_id: 1,
    quantity: 50,
    transaction_type: 'entrada',
    transaction_date: '2023-10-01'
  }];

  const typeColors = {
    entrada: 'success',
    salida: 'danger',
    ajuste: 'warning'
  };

  return (
    <div className="container mt-4">
      <h1>Transacciones de Inventario</h1>
      <Button variant="primary" onClick={() => setShowModal(true)}>
        Nueva Transacción
      </Button>

      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>ID</th>
            <th>Cantidad</th>
            <th>Tipo</th>
            <th>Fecha</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sampleData.map(t => (
            <tr key={t.transaction_id}>
              <td>{t.transaction_id}</td>
              <td>{t.quantity}</td>
              <td>
                <Badge bg={typeColors[t.transaction_type]}>
                  {t.transaction_type}
                </Badge>
              </td>
              <td>{t.transaction_date}</td>
              <td>
                <Button variant="warning" size="sm" className="me-2">Editar</Button>
                <Button variant="danger" size="sm">Eliminar</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Nueva Transacción</Modal.Title>
        </Modal.Header>
        <Form>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Transacción</Form.Label>
              <Form.Select>
                <option value="entrada">Entrada</option>
                <option value="salida">Salida</option>
                <option value="ajuste">Ajuste</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Cantidad</Form.Label>
              <Form.Control type="number" step="0.01" required />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Producto</Form.Label>
              <Form.Select>
                <option value="1">Producto 1</option>
                <option value="2">Producto 2</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Ubicación</Form.Label>
              <Form.Select>
                <option value="1">Almacén Principal</option>
                <option value="2">Bodega Secundaria</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Notas</Form.Label>
              <Form.Control as="textarea" rows={3} />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              Registrar
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </div>
  );
}