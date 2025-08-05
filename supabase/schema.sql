-- Schema for tracking scraped PDFs and extracted data

-- Table to track all PDFs we've found and their processing status
CREATE TABLE IF NOT EXISTS scraped_pdfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'found', -- found, downloading, downloaded, processing, processed, failed
    storage_path TEXT, -- Path in Supabase Storage
    file_size INTEGER,
    
    -- Timestamps
    found_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    download_started_at TIMESTAMP WITH TIME ZONE,
    downloaded_at TIMESTAMP WITH TIME ZONE,
    process_started_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    
    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    year INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM found_at)) STORED,
    month INTEGER GENERATED ALWAYS AS (EXTRACT(MONTH FROM found_at)) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for quick status lookups
CREATE INDEX idx_scraped_pdfs_status ON scraped_pdfs(status);
CREATE INDEX idx_scraped_pdfs_filename ON scraped_pdfs(filename);
CREATE INDEX idx_scraped_pdfs_year_month ON scraped_pdfs(year, month);

-- Table for extracted auction data (will expand based on your extraction logic)
CREATE TABLE IF NOT EXISTS auction_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pdf_id UUID REFERENCES scraped_pdfs(id) ON DELETE CASCADE,
    
    -- Property details
    case_number TEXT,
    property_description TEXT,
    erf_number TEXT,
    area TEXT,
    address TEXT,
    
    -- Sale details
    sale_date DATE,
    sale_time TIME,
    venue TEXT,
    reserve_price DECIMAL(12, 2),
    deposit_amount DECIMAL(12, 2),
    
    -- Parties involved
    sheriff_office TEXT,
    attorney_firm TEXT,
    attorney_contact TEXT,
    
    -- Metadata
    raw_text TEXT, -- Store raw extracted text for reference
    extraction_confidence DECIMAL(3, 2), -- 0.00 to 1.00
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for searching properties
CREATE INDEX idx_auction_properties_case_number ON auction_properties(case_number);
CREATE INDEX idx_auction_properties_sale_date ON auction_properties(sale_date);
CREATE INDEX idx_auction_properties_area ON auction_properties(area);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_scraped_pdfs_updated_at BEFORE UPDATE ON scraped_pdfs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_auction_properties_updated_at BEFORE UPDATE ON auction_properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for monitoring PDF processing status
CREATE OR REPLACE VIEW pdf_processing_status AS
SELECT 
    status,
    COUNT(*) as count,
    MIN(found_at) as oldest,
    MAX(found_at) as newest
FROM scraped_pdfs
GROUP BY status
ORDER BY status;