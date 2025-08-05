# Sheriff Auctions Data ETL Pipeline

Automated ETL pipeline for extracting Sheriff Auction data from SAFLII Legal Notice B documents.

## Features

- ✅ **Hourly Automated Checks**: Vercel Cron job checks SAFLII every hour for new Legal Notice B PDFs
- ✅ **Intelligent Deduplication**: Tracks all scraped PDFs to avoid re-downloading
- ✅ **Cloud Storage**: Stores PDFs in Supabase Storage (or Vercel Blob)
- ✅ **AWS Blocking Bypass**: Runs on Vercel infrastructure (not blocked like AWS)
- ✅ **Scalable Processing**: Serverless functions for PDF processing
- ✅ **Database Tracking**: Complete audit trail of all PDFs and their processing status

## Architecture

```
SAFLII Website
    ↓
[Hourly Cron Job] → Checks for new PDFs
    ↓
[Download Function] → Downloads new PDFs to cloud storage
    ↓
[Process Function] → Extracts data from PDFs
    ↓
[Supabase Database] → Stores structured auction data
```

## Setup Instructions

### 1. Prerequisites

- Vercel Pro account (for cron jobs)
- Supabase account (for database and storage)
- GitHub account

### 2. Database Setup

1. Create a new Supabase project
2. Run the SQL schema in `supabase/schema.sql` in your Supabase SQL editor
3. Get your Supabase URL and Service Role Key from project settings

### 3. GitHub Setup

```bash
# Clone this repo
git clone <your-repo-url>
cd sheriff-auctions-data-etl

# Create .env.local from template
cp .env.example .env.local
# Edit .env.local with your Supabase credentials
```

### 4. Vercel Deployment

1. Connect your GitHub repo to Vercel
2. Add environment variables in Vercel dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - `CRON_SECRET` (generate a random string)

3. Deploy to Vercel

### 5. Verify Cron Job

The cron job will run automatically every hour. You can also trigger it manually:

```bash
curl https://your-app.vercel.app/api/cron/hourly-check
```

## API Endpoints

- `/api/cron/hourly-check` - Cron job that checks for new PDFs (runs hourly)
- `/api/download-pdf` - Downloads a specific PDF to storage
- `/api/process-pdf` - Processes a PDF and extracts auction data
- `/api/check-new-pdfs` - Manual endpoint to check for new PDFs

## Monitoring

View processing status in Supabase:

```sql
-- Check PDF processing status
SELECT * FROM pdf_processing_status;

-- View recent PDFs
SELECT * FROM scraped_pdfs ORDER BY found_at DESC LIMIT 10;

-- Check failed downloads
SELECT * FROM scraped_pdfs WHERE status = 'download_failed';
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally with Vercel CLI
vercel dev
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SUPABASE_URL | Your Supabase project URL | Yes |
| SUPABASE_SERVICE_KEY | Supabase service role key | Yes |
| CRON_SECRET | Secret to protect cron endpoint | Yes |
| BLOB_READ_WRITE_TOKEN | Vercel Blob token (optional) | No |

## Troubleshooting

### PDFs not downloading?
- Check Vercel function logs for errors
- Verify Supabase storage bucket exists
- Check if the site is blocking Vercel IPs (unlikely)

### Cron not running?
- Verify you have Vercel Pro subscription
- Check cron configuration in vercel.json
- View cron execution in Vercel dashboard

## License

MIT