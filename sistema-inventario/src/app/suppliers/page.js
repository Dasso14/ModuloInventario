import { useState } from 'react';
import { Button, Table, Form, Modal } from 'react-bootstrap';

export default function Suppliers() {
  const [showModal, setShowModal] = useState(false);
  
  const sampleData = [{
    supplier_id: 1,
    name: 'Proveedor Ejemplo',
    contact_name: 'Juan Pérez',
    phone: '555-1234',
    email: 'juan@proveedor.com'
  }];

  return (
    <div className="container mt-4">
      <h1>Gestión de Proveedores</h1>
      <Button variant="primary" onClick={() => setShowModal(true)}>
        Nuevo Proveedor
      </Button>

      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Contacto</th>
            <th>Teléfono</th>
            <th>Email</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sampleData.map(s => (
            <tr key={s.supplier_id}>
              <td>{s.name}</td>
              <td>{s.contact_name}</td>
              <td>{s.phone}</td>
              <td>{s.email}</td>
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
          <Modal.Title>Nuevo Proveedor</Modal.Title>
        </Modal.Header>
        <Form>
          <Modal.Body>
            <div className="row">
              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label>Nombre del Proveedor</Form.Label>
                  <Form.Control type="text" required />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Nombre de Contacto</Form.Label>
                  <Form.Control type="text" required />
                </Form.Group>
              </div>

              <div className="col-md-6">
                <Form.Group className="mb-3">
                  <Form.Label>Teléfono</Form.Label>
                  <Form.Control type="tel" />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control type="email" />
                </Form.Group>
              </div>
            </div>

            <Form.Group className="mb-3">
              <Form.Label>Dirección</Form.Label>
              <Form.Control as="textarea" rows={2} />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Identificación Tributaria</Form.Label>
              <Form.Control type="text" />
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