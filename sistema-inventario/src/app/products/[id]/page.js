"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation"; // Import useRouter if needed for future actions
import Link from "next/link";
import classNames from "classnames";
import { Container, Spinner, Alert, Button } from 'react-bootstrap'; // Import Bootstrap components
import { toast } from 'react-hot-toast'; // Import toast

// Import functions from your services
// Import the new getProductStockLevels function
import { getProductById, getProductStockLevels } from "../../../services/productService"; // Adjust the path if necessary
import { getAllCategories } from '../../../services/categoryService'; // Adjust the path if necessary
import { getAllSuppliers } from '../../../services/supplierService'; // Adjust the path if necessary

// Remove old simulated data imports
// import { getProductById, getStockLevelsByProductId, exampleCategories, exampleSuppliers } from "../../../../lib/product-data";


export default function ProductDetailPage() {
  const params = useParams();
  const productId = params.id ? parseInt(params.id, 10) : null;

  const [product, setProduct] = useState(undefined);
  const [categories, setCategories] = useState([]); // For category name lookup
  const [suppliers, setSuppliers] = useState([]); // For supplier name lookup
  const [stockLevels, setStockLevels] = useState([]); // State to hold fetched stock levels

  const [loading, setLoading] = useState(true); // Loading state for initial fetch
  const [error, setError] = useState(null); // Error state for initial fetch

  // Remove the simulated getLocationName helper as the API provides location_name
  // const getLocationName = (locationId) => { ... };


  useEffect(() => {
    const fetchData = async () => {
      if (productId === null || isNaN(productId)) {
        setError("ID de producto inválido en la URL.");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // Fetch product data
        const productResult = await getProductById(productId);
        if (!productResult || !productResult.success) {
          throw new Error(productResult?.message || `Producto con ID ${productId} no encontrado.`);
        }
        setProduct(productResult.data);

        // --- Fetch Stock Levels for this product ---
        const stockLevelsResult = await getProductStockLevels(productId);
        if (stockLevelsResult && stockLevelsResult.success) {
             setStockLevels(stockLevelsResult.data || []);
        } else {
             console.error("Error fetching stock levels:", stockLevelsResult?.message);
             // Decide if this error should block rendering or just show an empty table/message
             // For now, we'll let the rest of the page load and show an empty stock table.
             toast.error("Error al cargar niveles de stock."); // Optional: show a toast
             setStockLevels([]); // Ensure state is an empty array on error
        }
        // --- End Fetch Stock Levels ---


        // Fetch categories and suppliers for name lookup (can be fetched in parallel with stock)
        const [categoriesResult, suppliersResult] = await Promise.all([
            getAllCategories(),
            getAllSuppliers()
        ]);

        if (categoriesResult && categoriesResult.success) {
            setCategories(categoriesResult.data || []);
        } else {
            console.error("Error fetching categories for detail page:", categoriesResult?.message);
            toast.error("Error al cargar categorías para mostrar nombres."); // Optional: show a toast
        }

         if (suppliersResult && suppliersResult.success) {
            setSuppliers(suppliersResult.data || []);
         } else {
            console.error("Error fetching suppliers for detail page:", suppliersResult?.message);
             toast.error("Error al cargar proveedores para mostrar nombres."); // Optional: show a toast
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


  // Helper function to get category name from fetched categories
  const getCategoryName = (categoryId) => {
    if (categoryId === undefined || categoryId === null) return "N/A";
    // Find category in the fetched list
    const category = categories.find(
      (cat) => cat.id === categoryId // Assuming category object has 'id'
    );
    return category ? category.name : "Desconocida"; // Assuming category object has 'name'
  };

  // Helper function to get supplier name from fetched suppliers
  const getSupplierName = (supplierId) => {
    if (supplierId === undefined || supplierId === null) return "N/A";
     // Find supplier in the fetched list
    const supplier = suppliers.find(
      (sup) => sup.id === supplierId // Assuming supplier object has 'id'
    );
    return supplier ? supplier.name : "Desconocido"; // Assuming supplier object has 'name'
  };


  // --- Render Loading, Error, or Details ---

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
      <div
        className={classNames(
          "d-flex",
          "justify-content-between",
          "align-items-center",
          "mb-3"
        )}
      >
        <h1>Detalles del Producto: {product.name}</h1>
        <div> {/* Use a div to group buttons */}
            <Link href={`/products/${productId}/edit`} passHref> {/* Use productId from params */}
                <Button variant="warning" className="me-2">Editar</Button>
            </Link>
            {/* Add Delete button here, using deleteProduct service */}
            {/* Example:
            <Button variant="danger" onClick={() => handleDelete(productId)}>
                Eliminar
            </Button>
            */}
            <Link href="/products" passHref>
                <Button variant="secondary">Volver a la Lista</Button>
            </Link>
        </div>
      </div>

      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Información General</h5>
          <div className="row">
            <div className="col-md-6">
              <p>
                <strong>SKU:</strong> {product.sku || 'N/A'} 
              </p>
              <p>
                <strong>Nombre:</strong> {product.name || 'N/A'}
              </p>
              <p>
                <strong>Descripción:</strong> {product.description || "N/A"}
              </p>
              <p>
                <strong>Categoría:</strong>{" "}
                {getCategoryName(product.category_id)} {/* Use helper with fetched data */}
              </p>
              <p>
                <strong>Proveedor:</strong>{" "}
                {getSupplierName(product.supplier_id)} {/* Use helper with fetched data */}
              </p>
            </div>
            <div className="col-md-6">
              <p>
                <strong>Costo Unitario:</strong> ${typeof product.unit_cost === 'number' ? product.unit_cost.toFixed(2) : (product.unit_cost != null ? product.unit_cost : 'N/A')} {/* Check type and format */}
              </p>
              <p>
                <strong>Precio Unitario:</strong> $
                {typeof product.unit_price === 'number' ? product.unit_price.toFixed(2) : (product.unit_price != null ? product.unit_price : 'N/A')} {/* Check type and format */}
              </p>
              <p>
                <strong>Unidad de Medida:</strong> {product.unit_measure || 'N/A'} {/* Handle potential null */}
              </p>
              <p>
                <strong>Peso:</strong>{" "}
                {typeof product.weight === 'number' ? `${product.weight} kg` : "N/A"} {/* Check type and format */}
              </p>
              <p>
                <strong>Volumen:</strong>{" "}
                {typeof product.volume === 'number' ? `${product.volume} m³` : "N/A"} {/* Check type and format */}
              </p>
            </div>
          </div>
          <div className="row mt-3">
            <div className="col">
              <p>
                <strong>Stock Mínimo:</strong> {product.min_stock !== null ? product.min_stock : 'N/A'} {/* Handle potential null */}
              </p>
              <p>
                <strong>Stock Máximo:</strong>{" "}
                {product.max_stock !== null ? product.max_stock : "N/A"} {/* Handle potential null */}
              </p>
              <p>
                <strong>Estado:</strong>{" "}
                {product.is_active ? "Activo" : "Inactivo"} {/* Assuming boolean */}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stock Levels Section - Now using fetched data */}
      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Niveles de Stock por Ubicación</h5>
          {stockLevels.length > 0 ? (
            <table className="table table-striped table-bordered table-hover table-sm">
              <thead>
                <tr>
                  <th>Ubicación</th>
                  <th>Cantidad</th>
                  <th>Última Actualización</th> 
                </tr>
              </thead>
              <tbody>
                {stockLevels.map((sl) => (
                  // Assuming stock level object from API has 'id', 'location_name', 'quantity', 'last_updated'
                  <tr key={sl.id}>
                    <td>{sl.location_name || 'Desconocida'}</td> 
                    <td>{sl.quantity !== null ? sl.quantity : 'N/A'}</td> 
                     <td>{sl.last_updated ? new Date(sl.last_updated).toLocaleString() : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            // Message if no stock levels are found
            <p className="text-muted">No hay registros de stock por ubicación para este producto.</p>
          )}
        </div>
      </div>

      <div className={classNames("card", "mb-4")}>
        <div className="card-body">
          <h5 className="card-title">Códigos de Barras</h5>
          <p className="text-muted">
            Aquí se listarían y gestionarían los códigos de barras asociados a
            este producto.
          </p>
          <Button variant="outline-primary" size="sm" disabled> {/* Disabled as functionality is not implemented */}
            Agregar Código de Barras
          </Button>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h5 className="card-title">Historial de Transacciones</h5>
          <p className="text-muted">
            Aquí se listarían las transacciones de inventario
            (`inventory_transactions`) para este producto.
          </p>
           {/* Link to transactions report - assuming it exists */}
          <Link href={`/reports/transactions?productId=${productId}`}> {/* Use productId from params */}
            Ver todas las transacciones de este producto
          </Link>
        </div>
      </div>
    </Container>
  );
}
