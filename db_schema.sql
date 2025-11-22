-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS production_logs CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;

-- Create Suppliers table
CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    eligibility JSONB,
    description JSONB,
    reliability_score INT DEFAULT 0
);

-- Create Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL,
    amount INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    quality JSONB,
    status VARCHAR(50) NOT NULL,
    
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
);

-- Create Production_logs table
CREATE TABLE production_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    product_type VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_transactions_supplier ON transactions(supplier_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_production_logs_supplier ON production_logs(supplier_id);
CREATE INDEX idx_production_logs_date ON production_logs(date);