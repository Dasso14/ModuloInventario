// app/products/page.js
"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { toast } from 'react-hot-toast'; // Asegúrate de tener react-hot-toast instalado
import { Container, Spinner, Alert, Button } from 'react-bootstrap'; // Import Bootstrap components if using them for loading/error

// Importamos las funciones de los servicios
// Import getProductStockLevels
import { getAllProducts, deleteProduct, getProductStockLevels } from '../../services/productService'; // Adjust the path if necessary
import { getAllCategories } from '../../services/categoryService'; // Adjust the path if necessary
import { getAllSuppliers } from '../../services/supplierService'; // Adjust the path if necessary

// Remove old simulated data imports
// import { getProducts, exampleCategories, exampleSuppliers } from "../../../lib/product-data";
// import classNames from "classnames"; // Keep if using classNames elsewhere


export default function ProductListPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]); // For category name lookup
  const [suppliers, setSuppliers] = useState([]); // For supplier name lookup

  const [loading, setLoading] = useState(true); // Loading state for initial fetch
  // New state to indicate if stock levels are being fetched after initial list
  const [loadingStock, setLoadingStock] = useState(false);
  const [error, setError] = useState(null); // Error state for initial fetch

  // Estados para paginación y ordenación (se mantienen)
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');

  // Note: Search functionality was removed in the previous step.
  // If you need it back, you'll need to re-add the state, input, and backend logic.


  const fetchProducts = async () => {
    setLoading(true);
    setError(null); // Limpiar error previo
    try {
      // Construir parámetros de consulta SOLO para paginación y ordenación
      const queryParams = new URLSearchParams();
      queryParams.append('page', currentPage.toString());
      queryParams.append('sort_by', sortField);
      queryParams.append('sort_dir', sortDirection);
      // Add per_page if your API supports it and you want to control it from frontend
      // queryParams.append('per_page', '10'); // Example: 10 items per page

      const queryString = '?' + queryParams.toString();

      // Fetch products using the service (Step 1: Get the list of products)
      // Assumes the service/API returns { success: boolean, data: [...], pagination?: {...}, message?: string }
      const productsResult = await getAllProducts(queryString);

      if (productsResult && productsResult.success) {
        const productsList = productsResult.data || [];
        setProducts(productsList); // Set the initial product list

        // If the API returns pagination metadata
        if (productsResult.pagination) {
          setTotalPages(productsResult.pagination.total_pages || 1);
        } else {
          // If the API doesn't return pagination, assume it's a single page
          setTotalPages(1);
        }
        setError(null); // Clear any previous errors

        // --- Step 2: Fetch Stock Levels for each product ---
        if (productsList.length > 0) {
             setLoadingStock(true); // Indicate that stock is being loaded
             const productsWithStock = await Promise.all(
                 productsList.map(async (product) => {
                     try {
                         const stockResult = await getProductStockLevels(product.id); // Assuming product object has 'id'
                         let totalStock = 0;
                         if (stockResult && stockResult.success && Array.isArray(stockResult.data)) {
                             // Sum quantities from all locations for this product
                             totalStock = stockResult.data.reduce((sum, stockItem) => {
                                 // Ensure quantity is a number before summing
                                 const quantity = parseFloat(stockItem.quantity);
                                 return sum + (isNaN(quantity) ? 0 : quantity);
                             }, 0);
                         } else {
                             console.error(`Error fetching stock for product ${product.id}:`, stockResult?.message);
                             // totalStock remains 0 or handle error differently
                         }
                         // Return the original product object with the added totalStock property
                         return { ...product, total_stock: totalStock };
                     } catch (stockErr) {
                         console.error(`Network error fetching stock for product ${product.id}:`, stockErr);
                         // Return product with error indicator or default stock
                         return { ...product, total_stock: 'Error' }; // Indicate error in UI
                     }
                 })
             );
             setProducts(productsWithStock); // Update state with products including total stock
             setLoadingStock(false); // Stock loading finished
        } else {
            setLoadingStock(false); // No products to fetch stock for
        }
        // --- End Step 2 ---


      } else {
        // Handle case where initial product list fetch fails
        throw new Error(productsResult?.message || 'Error desconocido al cargar productos');
      }
    } catch (err) {
      console.error('Error fetching products or stock:', err);
      setError(err.message);
      toast.error('Error al cargar los productos');
      setProducts([]); // Clear the list on error
      setTotalPages(1); // Reset pagination on error
      setLoadingStock(false); // Ensure stock loading is off on main error
    } finally {
      setLoading(false); // Initial product list loading finished
    }
  };

  // Fetch categories and suppliers for name lookup (can be done once on mount)
   const fetchRelatedData = async () => {
       try {
           const [categoriesResult, suppliersResult] = await Promise.all([
               getAllCategories(),
               getAllSuppliers()
           ]);

           if (categoriesResult && categoriesResult.success) {
               setCategories(categoriesResult.data || []);
           } else {
               console.error("Error fetching categories for product list:", categoriesResult?.message);
               // Decide if this error should block rendering or just show N/A
           }

            if (suppliersResult && suppliersResult.success) {
               setSuppliers(suppliersResult.data || []);
            } else {
               console.error("Error fetching suppliers for product list:", suppliersResult?.message);
               // Decide if this error should block rendering or just show N/A
            }
       } catch (err) {
           console.error('Error fetching related data for product list:', err);
           // Decide if this error should block rendering or just show N/A
       }
   };


  // Effect to fetch products (and then stock) when pagination/sorting changes
  useEffect(() => {
    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, sortField, sortDirection]); // Dependencies: fetch when these change

  // Effect to fetch categories and suppliers once on mount
   useEffect(() => {
       fetchRelatedData();
   }, []); // Empty dependency array

  const handleDelete = async (id) => {
    if (confirm(`¿Está seguro de eliminar el producto con ID ${id}?`)) {
      // Optional: set a loading state specifically for the item being deleted
      // setLoading(true); // Or manage loading state per item/row
      try {
        // Use the deleteProduct service function
        // Assumes the service returns { success: boolean, message?: string }
        const result = await deleteProduct(id);

        if (result && result.success) {
          // Update the list after deleting without a full refetch
          setProducts(products.filter(product => (product.product_id || product.id) !== id)); // Assuming product object has 'id' or 'product_id'
          toast.success(`Producto ${id} eliminado correctamente`);
           // Optional: If the deletion affects pagination (e.g., last item on a page), you might need to refetch
           // fetchProducts();
        } else {
           const errorMessage = result?.message || 'Error al eliminar el producto';
           throw new Error(errorMessage);
        }
      } catch (err) {
        console.error('Error deleting product:', err);
        toast.error(err.message || 'Error al eliminar el producto');
      } finally {
        // If you are not refetching the list, hide the global loading here
         // setLoading(false);
      }
    }
  };


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


  const handleSort = (field) => {
    // If it's the same field, reverse direction, otherwise sort ascending
    setSortDirection(field === sortField && sortDirection === 'asc' ? 'desc' : 'asc');
    setSortField(field);
    setCurrentPage(1); // Reset to the first page when changing sort
  };

  const renderSortIcon = (field) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages && !loading && !loadingStock) { // Prevent page change if loading anything
      setCurrentPage(newPage);
    }
  };

   // Show a spinner if loading AND the list is empty
  if (loading && products.length === 0 && !error) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
        <p className="mt-2">Cargando productos...</p>
      </Container>
    );
  }

  return (
    <Container className="py-4"> {/* Added Container for consistent padding */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Lista de Productos</h1>
        <Link href="/products/create" passHref>
          <Button variant="primary">
            <i className="bi bi-plus-circle me-2"></i>Crear Nuevo Producto
          </Button>
        </Link>
      </div>

      {error && (
        <Alert variant="danger" role="alert">
          {error}
        </Alert>
      )}

      {/* Show small spinner if data exists but is refreshing (e.g., pagination, sorting) */}
      {/* Also show if loading stock levels after the list is loaded */}
      {(loading || loadingStock) && products.length > 0 && (
         <div className="text-center mb-3">
             <Spinner animation="border" size="sm" role="status" className="text-primary">
                <span className="visually-hidden">Cargando...</span>
             </Spinner>
             <span className="ms-2 text-muted">{loadingStock ? 'Cargando stock...' : 'Actualizando lista...'}</span> {/* More specific message */}
         </div>
      )}

      {/* Message if no products found after loading and no error */}
      {!loading && !error && products.length === 0 && (
           <Alert variant="info" className="text-center" role="alert">
               No se encontraron productos.
           </Alert>
      )}


      {/* The table is only displayed if there are products */}
      {products.length > 0 && (
        <div className="table-responsive">
          <table className="table table-striped table-bordered table-hover">
            <thead className="table-light">
              <tr>
          
                <th onClick={() => handleSort('sku')} style={{ cursor: 'pointer' }}>
                  SKU {renderSortIcon('sku')}
                </th>
                <th onClick={() => handleSort('name')} style={{ cursor: 'pointer' }}>
                  Nombre {renderSortIcon('name')}
                </th>

                <th>Categoría</th>
                <th>Proveedor</th>
                <th onClick={() => handleSort('unit_price')} style={{ cursor: 'pointer' }}>
                  Precio Unitario {renderSortIcon('unit_price')}
                </th>
                
                <th>Stock Total</th>
                <th onClick={() => handleSort('is_active')} style={{ cursor: 'pointer' }}>
                  Activo {renderSortIcon('is_active')}
                </th>
                <th className="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                // Assuming product object has a unique identifier like 'product_id' or 'id'
                <tr key={product.product_id || product.id}>
                  <td>{product.sku || 'N/A'}</td> 
                  <td>{product.name || 'N/A'}</td> 
                  <td>{getCategoryName(product.category_id)}</td>
                  <td>{getSupplierName(product.supplier_id)}</td> 
                 
                  <td>${typeof product.unit_price === 'number' ? product.unit_price.toFixed(2) : (product.unit_price != null ? product.unit_price : 'N/A')}</td>
          
                  <td>
                      {product.hasOwnProperty('total_stock') ?
                          (product.total_stock === 'Error' ?
                             <span className="text-danger">Error</span> :
                             (product.total_stock !== null ? product.total_stock : '0') // Show 0 if stock is null/undefined after fetch
                          )
                          : // If total_stock property is not yet added (meaning stock is still loading)
                          (loadingStock ?
                             <Spinner animation="border" size="sm" /> :
                             'N/A' // Should not happen if loadingStock is handled correctly, but as fallback
                          )
                      }
                  </td>
                  {/* --------------------------------------------------- */}
                  {/* Assuming boolean */}
                  <td>{product.is_active ? "Sí" : "No"}</td>
                  <td className="text-center">
                    <div className="btn-group" role="group">
                     
                      <Link href={`/products/${product.product_id || product.id}`} passHref>
                        <Button variant="info" size="sm" className="me-2" disabled={loading || loadingStock}>Ver</Button> {/* Disable while loading anything */}
                      </Link>
                      <Link href={`/products/${product.product_id || product.id}/edit`} passHref>
                        <Button variant="warning" size="sm" className="me-2" disabled={loading || loadingStock}>Editar</Button> {/* Disable while loading anything */}
                      </Link>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(product.product_id || product.id)} // Use product.id or product_id for delete
                        disabled={loading || loadingStock} // Disable while loading anything
                      >
                        Eliminar
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}


      {/* Paginación only shown if there's more than 1 page */}
      {totalPages > 1 && (
        <nav aria-label="Navegación de páginas" className="mt-4">
          <ul className="pagination justify-content-center">
            <li className={`page-item ${currentPage === 1 || loading || loadingStock ? 'disabled' : ''}`}>
              <Button className="page-link" onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1 || loading || loadingStock} aria-label="Anterior">
                &laquo; Anterior
              </Button>
            </li>

            {/* Generate page buttons dynamically */}
            {/* Simplified for brevity; consider ellipsis for many pages */}
            {[...Array(totalPages).keys()].map(page => (
              <li key={page + 1} className={`page-item ${currentPage === page + 1 ? 'active' : ''} ${loading || loadingStock ? 'disabled' : ''}`}>
                <Button className="page-link" onClick={() => handlePageChange(page + 1)} disabled={loading || loadingStock}>
                  {page + 1}
                </Button>
              </li>
            ))}

            <li className={`page-item ${currentPage === totalPages || loading || loadingStock ? 'disabled' : ''}`}>
              <Button className="page-link" onClick={() => handlePageChange(currentPage + 1)} disabled={currentPage === totalPages || loading || loadingStock} aria-label="Siguiente">
                Siguiente &raquo;
              </Button>
            </li>
          </ul>
        </nav>
      )}
       {/* Add results info if not error and not loading after initial load */}
       {!loading && !error && products.length > 0 && (
           <div className="text-center mt-3 text-muted">
               Mostrando {products.length} resultados en esta página. Total de páginas: {totalPages}.
           </div>
       )}
    </Container>
  );
}
