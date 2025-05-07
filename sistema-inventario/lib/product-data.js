// lib/data-mocks.js

// Datos de categorías de ejemplo
export const exampleCategories = [
    { category_id: 1, name: 'Electrónica' },
    { category_id: 2, name: 'Computadoras' },
    { category_id: 3, name: 'Accesorios' },
];

// Datos de proveedores de ejemplo
export const exampleSuppliers = [
    { supplier_id: 101, name: 'Tech Global' },
    { supplier_id: 102, name: 'Office Supplies Co.' },
];

// Datos de ubicaciones de ejemplo
export const exampleLocations = [
    { location_id: 1, name: 'Almacén Principal', address: 'Calle Falsa 123' },
    { location_id: 2, name: 'Tienda 1', address: 'Av. Siempreviva 742' },
    { location_id: 3, name: 'Bodega Trasera', address: 'Calle Desconocida 456' },
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


// --- Nuevos Datos de Reportes ---
export const exampleUsers = [ // Mock simple de usuarios
    { user_id: 1, name: 'Admin User' },
    { user_id: 2, name: 'Warehouse Staff' },
];

export const exampleInventoryTransactions = [
    { transaction_id: 101, product_id: 1, location_id: 1, quantity: 20, transaction_type: 'entrada', transaction_date: '2025-05-06T10:00:00Z', reference_number: 'PO12345', notes: 'Compra inicial', user_id: 1, related_transaction: null, created_at: '2025-05-06T10:00:00Z' },
    { transaction_id: 102, product_id: 2, location_id: 1, quantity: 100, transaction_type: 'entrada', transaction_date: '2025-05-05T09:00:00Z', reference_number: 'PO12340', notes: 'Compra a Tech Global', user_id: 1, related_transaction: null, created_at: '2025-05-05T09:00:00Z' },
    { transaction_id: 103, product_id: 2, location_id: 2, quantity: 15, transaction_type: 'salida', transaction_date: '2025-05-06T14:00:00Z', reference_number: 'SO9876', notes: 'Venta online', user_id: 2, related_transaction: null, created_at: '2025-05-06T14:00:00Z' },
    { transaction_id: 104, product_id: 1, location_id: 2, quantity: 5, transaction_type: 'salida', transaction_date: '2025-05-06T11:00:00Z', reference_number: 'SO9870', notes: 'Venta minorista', user_id: 2, related_transaction: null, created_at: '2025-05-06T11:00:00Z' },
    { transaction_id: 105, product_id: 3, location_id: 1, quantity: -5, transaction_type: 'ajuste', transaction_date: '2025-05-04T16:00:00Z', reference_number: null, notes: 'Conteo físico: 5 unidades faltantes', user_id: 1, related_transaction: null, created_at: '2025-05-04T16:00:00Z' },
    // ... más transacciones
];

export const exampleLocationTransfers = [
    { transfer_id: 1, product_id: 2, from_location_id: 1, to_location_id: 2, quantity: 8, transfer_date: '2025-05-06T16:00:00Z', notes: 'Traslado para reabastecer tienda', user_id: 2, created_at: '2025-05-06T16:00:00Z' },
     { transfer_id: 2, product_id: 3, from_location_id: 1, to_location_id: 3, quantity: 10, transfer_date: '2025-05-05T10:30:00Z', notes: 'Traslado a bodega para almacenamiento', user_id: 1, created_at: '2025-05-05T10:30:00Z' },
    // ... más transferencias
];



// Funciones de utilidad para simular la "API"
export const getProducts = () => exampleProducts;
export const getProductById = (id) => exampleProducts.find(p => p.product_id === id);
export const getStockLevels = () => exampleStockLevels;
export const getStockLevelsByProductId = (productId) => exampleStockLevels.filter(sl => sl.product_id === productId);
export const getLocations = () => exampleLocations;
export const getLocationById = (id) => exampleLocations.find(loc => loc.location_id === id);
export const getCategories = () => exampleCategories;
export const getCategoryById = (id) => exampleCategories.find(cat => cat.category_id === id);
export const getSuppliers = () => exampleSuppliers;
export const getSupplierById = (id) => exampleSuppliers.find(sup => sup.supplier_id === id);
export const getUsers = () => exampleUsers;
export const getUserById = (id) => exampleUsers.find(user => user.user_id === id);

export const getInventoryTransactions = (filters = {}) => {
    let transactions = exampleInventoryTransactions;
    // Implementar lógica de filtrado básica si es necesario para los reportes
    // Ejemplo: filtrar por productId
    if (filters.productId) {
         const prodId = parseInt(filters.productId, 10);
         transactions = transactions.filter(tx => tx.product_id === prodId);
    }
    // Puedes añadir más filtros (locationId, type, date range, etc.)
    return transactions;
};
export const getLocationTransfers = (filters = {}) => {
     let transfers = exampleLocationTransfers;
     // Implementar lógica de filtrado básica
     return transfers;
};

// --- Funciones auxiliares para obtener nombres ---
export const getCategoryName = (categoryId) => {
    const category = exampleCategories.find(cat => cat.category_id === categoryId);
    return category ? category.name : 'Desconocida';
};
export const getSupplierName = (supplierId) => {
    const supplier = exampleSuppliers.find(sup => sup.supplier_id === supplierId);
    return supplier ? supplier.name : 'Desconocido';
};
export const getLocationName = (locationId) => {
    const location = exampleLocations.find(loc => loc.location_id === locationId);
    return location ? location.name : 'Desconocida';
};
export const getProductName = (productId) => {
    const product = exampleProducts.find(p => p.product_id === productId);
    return product ? `${product.sku} - ${product.name}` : 'Producto Desconocido';
};
export const getUserName = (userId) => {
    const user = exampleUsers.find(user => user.user_id === userId);
    return user ? user.name : 'Usuario Desconocido';
};