# Sheriff Auctions Data ETL Pipeline

Simple web scraper to check SAFLII for Legal Notice B documents.

## Features

- ✅ **Hourly Automated Checks**: Vercel Cron job checks SAFLII every hour for Legal Notice B PDFs
- ✅ **AWS Blocking Bypass**: Runs on Vercel infrastructure (not blocked like AWS)
- ✅ **Simple API**: JSON endpoints to check for PDFs

## Architecture

```
SAFLII Website
    ↓
[Hourly Cron Job] → Checks for Legal Notice B PDFs and returns list
    ↓
[Manual Check API] → On-demand check for testing
```

## Setup Instructions

### 1. Prerequisites

- Vercel account (free tier works for basic functionality)
- GitHub account

### 2. GitHub Setup

```bash
# Clone this repo
git clone https://github.com/GustavBouwer/sheriff-auctions-data-etl.git
cd sheriff-auctions-data-etl
```

### 3. Vercel Deployment

1. Connect your GitHub repo to Vercel
2. Deploy to Vercel

### 4. Test the API

The cron job will run automatically every hour. You can also test manually:

```bash
# Check for PDFs manually
curl https://your-app.vercel.app/api/check-new-pdfs

# Cron job endpoint (runs hourly)
curl https://your-app.vercel.app/api/cron/hourly-check
```

## API Endpoints

- `/api/cron/hourly-check` - Cron job that checks for Legal Notice B PDFs (runs hourly)
- `/api/check-new-pdfs` - Manual endpoint to check for PDFs

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
| CRON_SECRET | Secret to protect cron endpoint | No |

## Troubleshooting

### Cron not running?
- Check cron configuration in vercel.json
- View cron execution in Vercel dashboard

### Site blocking requests?
- The scraper uses browser-like headers to avoid blocking
- Vercel infrastructure should bypass most AWS blocks

## License

MIT