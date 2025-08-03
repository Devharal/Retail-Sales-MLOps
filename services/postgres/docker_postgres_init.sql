-- Create sales table
CREATE TABLE IF NOT EXISTS rossman_sales (
    id SERIAL PRIMARY KEY,
    store INTEGER NOT NULL,
    dayofweek INTEGER,
    date DATE NOT NULL,
    sales FLOAT,
    customers INTEGER,
    open INTEGER,
    promo INTEGER,
    stateholiday VARCHAR(1),
    schoolholiday INTEGER,
    productname VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create forecast results table
CREATE TABLE IF NOT EXISTS forecast_results (
    id SERIAL PRIMARY KEY ,
    store INTEGER NOT NULL ,
    date DATE NOT NULL ,
    predicted_sales FLOAT ,
    actual_sales FLOAT ,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Create indices for better query performance
CREATE INDEX idx_sales_store_date ON rossman_sales ( store , date ) ;
CREATE INDEX idx_forecast_store_date ON forecast_results ( store , date ) ;