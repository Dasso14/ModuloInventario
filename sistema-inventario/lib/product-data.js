// lib/product-data.js

// Datos de categorías de ejemplo (solo para referencia visual)
const exampleCategories = [
    { category_id: 1, name: 'Electrónica' },
    { category_id: 2, name: 'Computadoras' },
    { category_id: 3, name: 'Accesorios' },
];

// Datos de proveedores de ejemplo (solo para referencia visual)
const exampleSuppliers = [
    { supplier_id: 101, name: 'Tech Global' },
    { supplier_id: 102, name: 'Office Supplies Co.' },
];

// Datos de productos de ejemplo
export const exampleProducts = [
    {
        product_id: 1,
        sku: 'PROD001',
        name: 'Laptop ABC',
        description: 'Laptop de alto rendimiento',
        category_id: 2, // Computadoras
        supplier_id: 101, // Tech Global
        unit_cost: 800.00,
        unit_price: 1200.00,
        unit_measure: 'unidad',
        weight: 2.5,
        volume: 0.01,
        min_stock: 10,
        max_stock: 50,
        is_active: true,
    },
    {
        product_id: 2,
        sku: 'PROD002',
        name: 'Mouse Óptico XYZ',
        description: 'Mouse ergonómico inalámbrico',
        category_id: 3, // Accesorios
        supplier_id: 101, // Tech Global
        unit_cost: 15.00,
        unit_price: 25.00,
        unit_measure: 'unidad',
        weight: 0.1,
        volume: 0.0001,
        min_stock: 20,
        max_stock: 100,
        is_active: true,
    },
     {
        product_id: 3,
        sku: 'PROD003',
        name: 'Cable HDMI 2m',
        description: 'Cable HDMI de 2 metros',
        category_id: 3, // Accesorios
        supplier_id: 102, // Office Supplies Co.
        unit_cost: 5.00,
        unit_price: 10.00,
        unit_measure: 'unidad',
        weight: 0.05,
        volume: 0.00005,
        min_stock: 30,
        max_stock: null,
        is_active: true,
    },
    {
        product_id: 4,
        sku: 'PROD004',
        name: 'Monitor 27 pulgadas',
        description: 'Monitor LED de 27 pulgadas',
        category_id: 1, // Electrónica
        supplier_id: 101, // Tech Global
        unit_cost: 200.00,
        unit_price: 350.00,
        unit_measure: 'unidad',
        weight: 4.0,
        volume: 0.05,
        min_stock: 5,
        max_stock: 20,
        is_active: true,
    },
     {
        product_id: 5,
        sku: 'PROD005',
        name: 'Teclado Mecánico',
        description: 'Teclado mecánico retroiluminado',
        category_id: 3, // Accesorios
        supplier_id: 101, // Tech Global
        unit_cost: 50.00,
        unit_price: 80.00,
        unit_measure: 'unidad',
        weight: 0.8,
        volume: 0.005,
        min_stock: 15,
        max_stock: null,
        is_active: false, // Ejemplo de producto inactivo
    },
];

// Datos de stock de ejemplo (simplificado: solo algunos productos en algunas ubicaciones)
export const exampleStockLevels = [
    { stock_id: 1, product_id: 1, location_id: 1, quantity: 15 }, // Laptop ABC en Ubicación 1
    { stock_id: 2, product_id: 1, location_id: 2, quantity: 5 },  // Laptop ABC en Ubicación 2 (Bajo stock si min_stock=10)
    { stock_id: 3, product_id: 2, location_id: 1, quantity: 80 }, // Mouse XYZ en Ubicación 1
    { stock_id: 4, product_id: 2, location_id: 2, quantity: 12 }, // Mouse XYZ en Ubicación 2 (Bajo stock si min_stock=20)
    { stock_id: 5, product_id: 3, location_id: 1, quantity: 25 }, // Cable HDMI en Ubicación 1 (Bajo stock si min_stock=30)
    { stock_id: 6, product_id: 4, location_id: 1, quantity: 8 },  // Monitor 27 en Ubicación 1
];

// Funciones de utilidad para simular la "API"
export const getProducts = () => exampleProducts;
export const getProductById = (id) => exampleProducts.find(p => p.product_id === id);
export const getStockLevelsByProductId = (productId) => exampleStockLevels.filter(sl => sl.product_id === productId);

// Nota: Las funciones para crear/editar/eliminar no se implementan aquí, solo la lectura.
// En un sistema real, harías llamadas a una API (rutas de API de Next.js o un backend separado)
// para interactuar con la base de datos.