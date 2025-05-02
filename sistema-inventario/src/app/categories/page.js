import { useState } from 'react';
import { Button, Table, Form, Modal } from 'react-bootstrap';

export default function Categories() {
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  
  // Datos de ejemplo
  const sampleData = [
    { category_id: 1, name: 'Electrónicos', parent_id: null, description: 'Dispositivos electrónicos' },
    { category_id: 2, name: 'Computadoras', parent_id: 1, description: 'Equipos de computación' }
  ];

  return (
    <div className="container mt-4">
      <h1>Gestión de Categorías</h1>
      <Button variant="primary" onClick={() => setShowModal(true)}>
        Nueva Categoría
      </Button>

      <Table striped bordered hover className="mt-3">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Categoría Padre</th>
            <th>Descripción</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sampleData.map((cat) => (
            <tr key={cat.category_id}>
              <td>{cat.category_id}</td>
              <td>{cat.name}</td>
              <td>{cat.parent_id || '-'}</td>
              <td>{cat.description}</td>
              <td>
                <Button variant="warning" size="sm" className="me-2"
                  onClick={() => { setEditMode(true); setShowModal(true); }}>
                  Editar
                </Button>
                <Button variant="danger" size="sm">Eliminar</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{editMode ? 'Editar' : 'Nueva'} Categoría</Modal.Title>
        </Modal.Header>
        <Form>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Nombre</Form.Label>
              <Form.Control type="text" required />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Categoría Padre</Form.Label>
              <Form.Select>
                <option value="">Ninguna</option>
                {sampleData.map(cat => (
                  <option key={cat.category_id} value={cat.category_id}>
                    {cat.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

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