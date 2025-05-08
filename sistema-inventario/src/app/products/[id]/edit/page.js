"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Container, Form, Button, Card, Row, Col, Spinner, Alert } from 'react-bootstrap';
import Link from 'next/link';
import { toast } from 'react-hot-toast'; // Assuming you have react-hot-toast installed

// Import functions from your services
import { getProductById, updateProduct } from '../../../../services/productService'; // Adjust the path if necessary
import { getAllCategories } from '../../../../services/categoryService'; // Adjust the path if necessary
import { getAllSuppliers } from '../../../../services/supplierService'; // Adjust the path if necessary

// Remove the old simulated data import
// import { getProductById, exampleCategories, exampleSuppliers } from '../../../../../lib/product-data';

export default function EditProductPage() {
  const router = useRouter();
  const params = useParams();
  const productId = params.id ? parseInt(params.id, 10) : null;

  const [product, setProduct] = useState(undefined); // Original product data
  const [categories, setCategories] = useState([]); // For category dropdown
  const [suppliers, setSuppliers] = useState([]); // For supplier dropdown

  const [loading, setLoading] = useState(true); // Loading state for initial fetch
  const [isSubmitting, setIsSubmitting] = useState(false); // Loading state for form submission
  const [error, setError] = useState(null); // Error state for initial fetch
  const [formError, setFormError] = useState(''); // Error state for form validation/submission

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
    const fetchData = async () => {
      if (productId === null || isNaN(productId)) {
        setError("ID de producto inválido en la URL.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      setFormError('');

      try {
        // Fetch product data
        const productResult = await getProductById(productId);
        if (!productResult || !productResult.success) {
          throw new Error(productResult?.message || `Producto con ID ${productId} no encontrado.`);
        }
        const foundProduct = productResult.data;
        setProduct(foundProduct);

        // Populate form data with fetched product data
        setFormData({
          sku: foundProduct.sku || '',
          name: foundProduct.name || '',
          description: foundProduct.description || '',
          // Ensure IDs are strings for select values
          category_id: foundProduct.category_id !== null ? foundProduct.category_id.toString() : '',
          supplier_id: foundProduct.supplier_id !== null ? foundProduct.supplier_id.toString() : '',
          unit_cost: foundProduct.unit_cost !== null ? foundProduct.unit_cost.toString() : '',
          unit_price: foundProduct.unit_price !== null ? foundProduct.unit_price.toString() : '',
          unit_measure: foundProduct.unit_measure || 'unidad',
          weight: foundProduct.weight !== null ? foundProduct.weight.toString() : '',
          volume: foundProduct.volume !== null ? foundProduct.volume.toString() : '',
          min_stock: foundProduct.min_stock !== null ? foundProduct.min_stock.toString() : '0',
          max_stock: foundProduct.max_stock !== null ? foundProduct.max_stock.toString() : '',
          is_active: foundProduct.is_active ?? true, // Default to true if null/undefined
        });

        // Fetch categories and suppliers for dropdowns
        const categoriesResult = await getAllCategories();
        if (categoriesResult && categoriesResult.success) {
          setCategories(categoriesResult.data || []);
        } else {
           console.error("Error fetching categories:", categoriesResult?.message);
           // Decide if this is a critical error or just a warning
           // setError(categoriesResult?.message || "Error al cargar categorías.");
           toast.error("Error al cargar categorías para el formulario.");
        }

        const suppliersResult = await getAllSuppliers();
         if (suppliersResult && suppliersResult.success) {
           setSuppliers(suppliersResult.data || []);
         } else {
            console.error("Error fetching suppliers:", suppliersResult?.message);
            // Decide if this is a critical error or just a warning
            // setError(suppliersResult?.message || "Error al cargar proveedores.");
            toast.error("Error al cargar proveedores para el formulario.");
         }


      } catch (err) {
        console.error('Error fetching product or related data:', err);
        setError(err.message || 'Error al cargar los datos del producto.');
        toast.error('Error al cargar los datos del producto.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [productId]); // Rerun effect if the product ID in the URL changes


  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    setFormData(prevState => ({
      ...prevState,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear form error when user starts typing/changing
    setFormError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setIsSubmitting(true);

    // Basic client-side validation (can add more)
    if (!formData.sku.trim() || !formData.name.trim() || !formData.category_id || !formData.supplier_id || formData.unit_cost === '' || formData.unit_price === '') {
        setFormError('Por favor, completa todos los campos obligatorios.');
        setIsSubmitting(false);
        return;
    }

    // Prepare data for API (convert numbers back, handle empty strings for optional fields)
    const dataToSubmit = {
        ...formData,
        category_id: parseInt(formData.category_id, 10),
        supplier_id: parseInt(formData.supplier_id, 10),
        unit_cost: parseFloat(formData.unit_cost),
        unit_price: parseFloat(formData.unit_price),
        // Convert optional number fields, send null if empty string
        weight: formData.weight !== '' ? parseFloat(formData.weight) : null,
        volume: formData.volume !== '' ? parseFloat(formData.volume) : null,
        min_stock: parseInt(formData.min_stock, 10),
        max_stock: formData.max_stock !== '' ? parseInt(formData.max_stock, 10) : null,
    };

    console.log('Datos a enviar a la API:', dataToSubmit);

    try {
      // Use the updateProduct service function
      const result = await updateProduct(productId, dataToSubmit);

      // Assuming the service/API returns { success: boolean, data?: {...}, message?: string }
      if (result && result.success) {
        toast.success('Producto actualizado correctamente');
        router.push(`/products/${productId}`); // Redirect to product detail page
      } else {
        // Handle API-specific errors (e.g., validation errors from backend)
        const errorMessage = result?.message || 'Error al actualizar el producto';
        setFormError(errorMessage);
        toast.error(errorMessage);
      }
    } catch (err) {
      console.error('Error updating product:', err);
      // Handle network errors or errors thrown by fetchApi
      const errorMessage = err.message || 'Error de comunicación con el servidor al actualizar';
      setFormError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- Render Loading, Error, or Form ---

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
        <p className="mt-2">Cargando datos del producto...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          <Alert.Heading>Error al cargar el producto</Alert.Heading>
          <p>{error}</p>
          <hr />
          <Link href="/products" passHref>
            <Button variant="danger">Volver a la Lista de Productos</Button>
          </Link>
        </Alert>
      </Container>
    );
  }

  // If no product found after loading (should be covered by error, but as a fallback)
  if (!product) {
     return (
         <Container className="py-5">
             <Alert variant="warning">
                 <Alert.Heading>Producto no disponible</Alert.Heading>
                 <p>No se pudo encontrar la información del producto solicitado.</p>
                 <hr />
                 <Link href="/products" passHref>
                     <Button variant="warning">Volver a la Lista de Productos</Button>
                 </Link>
             </Alert>
         </Container>
     );
  }


  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1>Editar Producto: {product.name}</h1>
        <Link href={`/products/${productId}`} passHref> {/* Use productId from params */}
          <Button variant="secondary">Cancelar</Button>
        </Link>
      </div>

      <Card>
        <Card.Body>
          {formError && <Alert variant="danger">{formError}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Row className="mb-3">
              <Form.Group as={Col} md="4" controlId="formSku"> {/* Added Col size */}
                <Form.Label>SKU <span className="text-danger">*</span></Form.Label>
                <Form.Control type="text" name="sku" value={formData.sku} onChange={handleChange} required maxLength="50" disabled={isSubmitting} />
              </Form.Group>
              <Form.Group as={Col} md="8" controlId="formName"> {/* Added Col size */}
                <Form.Label>Nombre <span className="text-danger">*</span></Form.Label>
                <Form.Control type="text" name="name" value={formData.name} onChange={handleChange} required maxLength="255" disabled={isSubmitting} />
              </Form.Group>
            </Row>

            <Form.Group className="mb-3" controlId="formDescription">
              <Form.Label>Descripción</Form.Label>
              <Form.Control as="textarea" rows={3} name="description" value={formData.description} onChange={handleChange} disabled={isSubmitting} />
            </Form.Group>

            <Row className="mb-3">
              <Form.Group as={Col} md="6" controlId="formCategory"> {/* Added Col size */}
                <Form.Label>Categoría <span className="text-danger">*</span></Form.Label>
                <Form.Select name="category_id" value={formData.category_id} onChange={handleChange} required disabled={isSubmitting || categories.length === 0}>
                  <option value="">Seleccione una categoría</option>
                  {/* Use fetched categories */}
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>{category.name}</option> 
                  ))}
                </Form.Select>
                 {categories.length === 0 && !loading && <Form.Text className="text-danger">No hay categorías disponibles.</Form.Text>}
              </Form.Group>

              <Form.Group as={Col} md="6" controlId="formSupplier"> {/* Added Col size */}
                <Form.Label>Proveedor <span className="text-danger">*</span></Form.Label>
                <Form.Select name="supplier_id" value={formData.supplier_id} onChange={handleChange} required disabled={isSubmitting || suppliers.length === 0}>
                  <option value="">Seleccione un proveedor</option>
                   {/* Use fetched suppliers */}
                  {suppliers.map(supplier => (
                    <option key={supplier.id} value={supplier.id}>{supplier.name}</option> 
                  ))}
                </Form.Select>
                 {suppliers.length === 0 && !loading && <Form.Text className="text-danger">No hay proveedores disponibles.</Form.Text>}
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} md="4" controlId="formUnitCost"> {/* Added Col size */}
                <Form.Label>Costo Unitario <span className="text-danger">*</span></Form.Label>
                <Form.Control type="number" step="0.01" name="unit_cost" value={formData.unit_cost} onChange={handleChange} required min="0" disabled={isSubmitting} />
              </Form.Group>
              <Form.Group as={Col} md="4" controlId="formUnitPrice"> {/* Added Col size */}
                <Form.Label>Precio Unitario <span className="text-danger">*</span></Form.Label>
                <Form.Control type="number" step="0.01" name="unit_price" value={formData.unit_price} onChange={handleChange} required min="0" disabled={isSubmitting} />
              </Form.Group>
              <Form.Group as={Col} md="4" controlId="formUnitMeasure"> {/* Added Col size */}
                <Form.Label>Unidad de Medida <span className="text-danger">*</span></Form.Label>
                <Form.Select name="unit_measure" value={formData.unit_measure} onChange={handleChange} required disabled={isSubmitting}>
                  <option value="unidad">Unidad</option>
                  <option value="litro">Litro</option>
                  <option value="kilogramo">Kilogramo</option>
                  <option value="metro">Metro</option>
                  <option value="caja">Caja</option>
                   {/* Add other units as needed */}
                </Form.Select>
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} md="6" controlId="formWeight"> {/* Added Col size */}
                <Form.Label>Peso (kg)</Form.Label>
                <Form.Control type="number" step="0.01" name="weight" value={formData.weight} onChange={handleChange} min="0" disabled={isSubmitting} />
              </Form.Group>
              <Form.Group as={Col} md="6" controlId="formVolume"> {/* Added Col size */}
                <Form.Label>Volumen (m³)</Form.Label>
                <Form.Control type="number" step="0.01" name="volume" value={formData.volume} onChange={handleChange} min="0" disabled={isSubmitting} />
              </Form.Group>
            </Row>

            <Row className="mb-3">
              <Form.Group as={Col} md="6" controlId="formMinStock"> {/* Added Col size */}
                <Form.Label>Stock Mínimo <span className="text-danger">*</span></Form.Label>
                <Form.Control type="number" name="min_stock" value={formData.min_stock} onChange={handleChange} required min="0" disabled={isSubmitting} />
              </Form.Group>
              <Form.Group as={Col} md="6" controlId="formMaxStock"> {/* Added Col size */}
                <Form.Label>Stock Máximo</Form.Label>
                <Form.Control type="number" name="max_stock" value={formData.max_stock} onChange={handleChange} min="0" disabled={isSubmitting} />
              </Form.Group>
            </Row>

            <Form.Group className="mb-3" controlId="formIsActive">
              <Form.Check
                type="checkbox"
                label="Producto Activo"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                disabled={isSubmitting}
              />
            </Form.Group>

            <Button variant="primary" type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Actualizando...
                </>
              ) : (
                'Actualizar Producto'
              )}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
}
