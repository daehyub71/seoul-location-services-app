# Vercel Environment Variables Setup Guide

This document lists all environment variables required for deploying the Seoul Location Services application to Vercel.

## Frontend Environment Variables

Configure these in your Vercel Frontend project settings (Settings → Environment Variables):

### Required Variables

| Variable Name | Description | Example Value | Where to Get |
|--------------|-------------|---------------|--------------|
| `VITE_KAKAO_MAP_API_KEY` | Kakao JavaScript API Key for map visualization | `your_kakao_javascript_key` | [Kakao Developers Console](https://developers.kakao.com/console/app) |
| `VITE_API_BASE_URL` | Backend API base URL | `https://your-backend.vercel.app` | Your Vercel Backend deployment URL |

### Optional Variables

| Variable Name | Description | Default Value |
|--------------|-------------|---------------|
| `VITE_APP_NAME` | Application name | `Seoul Location Services` |
| `VITE_APP_VERSION` | Application version | `1.0.0` |
| `VITE_DEFAULT_LAT` | Default map center latitude (Seoul City Hall) | `37.5665` |
| `VITE_DEFAULT_LON` | Default map center longitude | `126.9780` |
| `VITE_DEFAULT_ZOOM` | Default map zoom level | `5` |
| `VITE_ENABLE_DARK_MODE` | Enable dark mode feature | `false` |
| `VITE_ENABLE_LLM_RECOMMENDATIONS` | Enable LLM-based recommendations | `false` |
| `VITE_ENABLE_ANALYTICS` | Enable analytics tracking | `false` |
| `VITE_SENTRY_DSN` | Sentry error tracking DSN | (empty) |
| `VITE_GA_TRACKING_ID` | Google Analytics tracking ID | (empty) |

### Setting Up Kakao JavaScript API Key

1. Go to [Kakao Developers Console](https://developers.kakao.com/console/app)
2. Create a new application or select existing one
3. Go to **App Settings** → **Platform** → **Web**
4. Add your Vercel domain: `https://your-app.vercel.app`
5. Add local development domain: `http://localhost:5173`
6. Copy the **JavaScript Key** (NOT REST API Key!)
7. Save and wait 5-10 minutes for changes to propagate

---

## Backend Environment Variables

Configure these in your Vercel Backend project settings (Settings → Environment Variables):

### Required Variables - Database

| Variable Name | Description | Example Value | Where to Get |
|--------------|-------------|---------------|--------------|
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase Dashboard → Settings → API → anon/public |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (admin) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Supabase Dashboard → Settings → API → service_role (⚠️ Keep secret!) |
| `SUPABASE_DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres.xxx:password@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres` | Supabase Dashboard → Settings → Database → Connection string (Session mode) |

### Required Variables - Cache

| Variable Name | Description | Example Value | Where to Get |
|--------------|-------------|---------------|--------------|
| `UPSTASH_URL` | Upstash Redis REST URL | `https://xxx.upstash.io` | [Upstash Console](https://console.upstash.com/) → Database → REST API |
| `UPSTASH_TOKEN` | Upstash Redis REST token | `AbCdEfGhIjKlMnOpQrStUvWxYz...` | Upstash Console → Database → REST API |
| `REDIS_URL` | Redis URL (same as UPSTASH_URL) | `https://xxx.upstash.io` | Same as UPSTASH_URL |

### Required Variables - External APIs

| Variable Name | Description | Example Value | Where to Get |
|--------------|-------------|---------------|--------------|
| `SEOUL_API_KEY` | Seoul Open API authentication key | `your_seoul_api_key` | [Seoul Open Data Plaza](https://data.seoul.go.kr/) → 회원가입 → 인증키 신청 |
| `KAKAO_REST_API_KEY` | Kakao REST API key for geocoding | `your_kakao_rest_api_key` | [Kakao Developers Console](https://developers.kakao.com/console/app) → App Settings → REST API Key |

### Optional Variables - Configuration

| Variable Name | Description | Default Value |
|--------------|-------------|---------------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `API_VERSION` | API version prefix | `v1` |
| `REDIS_CACHE_TTL` | Cache TTL in seconds | `300` (5 minutes) |
| `CACHE_ENABLED` | Enable Redis caching | `true` |
| `COLLECTION_SCHEDULE_ENABLED` | Enable scheduled data collection | `false` (disable in serverless) |
| `COLLECTION_RETRY_COUNT` | API retry count on failure | `3` |
| `COLLECTION_TIMEOUT` | API request timeout (seconds) | `30` |
| `RATE_LIMIT_ENABLED` | Enable API rate limiting | `true` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit per minute | `100` |
| `CORS_ORIGINS_EXTRA` | Additional CORS origins (comma-separated) | (empty) |

### Optional Variables - Advanced Features

| Variable Name | Description | Example Value |
|--------------|-------------|---------------|
| `FIREBASE_DATABASE_URL` | Firebase Realtime Database URL | `https://xxx.firebaseio.com` |
| `FIREBASE_ADMIN_SDK_PATH` | Path to Firebase Admin SDK JSON | `./firebase-admin-sdk.json` |
| `OLLAMA_BASE_URL` | Ollama API base URL (not recommended for serverless) | `http://localhost:11434` |
| `OLLAMA_LLM_MODEL` | Ollama LLM model name | `llama3.1:8b` |
| `OLLAMA_EMBED_MODEL` | Ollama embedding model name | `bge-m3` |

---

## Setup Instructions

### 1. Frontend Deployment

```bash
# Navigate to frontend directory
cd frontend

# Install Vercel CLI (if not installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel (first time)
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? seoul-location-services-frontend
# - Directory? ./
# - Override settings? No

# Set environment variables in Vercel Dashboard
# Go to: https://vercel.com/dashboard
# → Select project → Settings → Environment Variables
# → Add all required frontend variables

# Deploy to production
vercel --prod
```

### 2. Backend Deployment

```bash
# Navigate to backend directory
cd backend

# Deploy to Vercel (first time)
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? seoul-location-services-backend
# - Directory? ./
# - Override settings? No

# Set environment variables in Vercel Dashboard
# Go to: https://vercel.com/dashboard
# → Select project → Settings → Environment Variables
# → Add all required backend variables

# Deploy to production
vercel --prod
```

### 3. Update Frontend API URL

After backend is deployed:

1. Get your backend Vercel URL (e.g., `https://seoul-location-services-backend.vercel.app`)
2. Go to Frontend project in Vercel Dashboard
3. Settings → Environment Variables
4. Update `VITE_API_BASE_URL` to your backend URL
5. Redeploy frontend: `vercel --prod`

### 4. Update Backend CORS

The backend is already configured to allow:
- `https://seoul-location-services.vercel.app`
- `https://*.vercel.app` (all Vercel preview deployments)

If you use a custom domain:
1. Go to Backend project in Vercel Dashboard
2. Settings → Environment Variables
3. Add `CORS_ORIGINS_EXTRA` with your custom domain (comma-separated)
4. Example: `https://myapp.com,https://www.myapp.com`

---

## Verification

### Frontend Health Check

Visit: `https://your-frontend.vercel.app`

Expected: Map should load with Kakao Map visualization

### Backend Health Check

Visit: `https://your-backend.vercel.app/health`

Expected JSON response:
```json
{
  "status": "healthy",
  "version": "v1",
  "environment": "production",
  "cache_enabled": true
}
```

### API Documentation

Visit: `https://your-backend.vercel.app/docs`

Expected: Interactive FastAPI/Swagger documentation

---

## Troubleshooting

### Frontend Issues

**Problem**: Map not loading
- **Solution**: Check `VITE_KAKAO_MAP_API_KEY` is correct JavaScript key (not REST API key)
- **Solution**: Verify domain is registered in Kakao Developer Console

**Problem**: Cannot connect to backend
- **Solution**: Check `VITE_API_BASE_URL` points to correct backend URL
- **Solution**: Verify backend CORS allows frontend domain

### Backend Issues

**Problem**: 500 Internal Server Error
- **Solution**: Check all required environment variables are set
- **Solution**: Verify Supabase and Redis credentials are correct
- **Solution**: Check logs in Vercel Dashboard → Deployments → View Function Logs

**Problem**: Database connection timeout
- **Solution**: Ensure `SUPABASE_DATABASE_URL` uses Session mode (not Transaction mode)
- **Solution**: Verify connection string includes correct password

**Problem**: Redis connection failed
- **Solution**: Check `UPSTASH_URL` and `UPSTASH_TOKEN` are correct
- **Solution**: Use REST API endpoint (https), not Redis protocol (redis://)

**Problem**: CORS errors
- **Solution**: Add frontend domain to `CORS_ORIGINS_EXTRA` environment variable
- **Solution**: Ensure domain includes protocol (https://) and no trailing slash

---

## Security Best Practices

1. **Never commit `.env` files** to git
2. **Use Vercel's secret environment variables** for sensitive data
3. **Rotate API keys** regularly (especially service_role keys)
4. **Enable Vercel's Password Protection** for preview deployments
5. **Monitor API usage** to detect unusual activity
6. **Use Supabase Row Level Security (RLS)** to protect data
7. **Enable Vercel's Web Analytics** for monitoring

---

## Monitoring and Maintenance

### Vercel Dashboard

- **Deployments**: View deployment history and logs
- **Analytics**: Monitor traffic and performance
- **Functions**: Check serverless function metrics
- **Logs**: Real-time function logs

### Supabase Dashboard

- **Table Editor**: View and manage data
- **SQL Editor**: Run custom queries
- **API**: Monitor API usage
- **Logs**: Database and API logs

### Upstash Dashboard

- **Database**: View Redis data
- **Analytics**: Monitor cache hit rate
- **Metrics**: Memory usage and operations

---

## Cost Estimation

### Vercel (Hobby Plan - Free)
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Serverless function execution included
- ⚠️ Function timeout: 10 seconds (upgrade for 60s)

### Supabase (Free Tier)
- ✅ 500 MB database storage
- ✅ 2 GB file storage
- ✅ 50,000 monthly active users
- ✅ Unlimited API requests

### Upstash Redis (Free Tier)
- ✅ 10,000 commands/day
- ✅ 256 MB storage
- ✅ 1 database

### Seoul Open API
- ✅ Free with API key
- ⚠️ Rate limits apply (varies by endpoint)

### Kakao API
- ✅ Free for map and geocoding
- ⚠️ Rate limits: 300,000 requests/day

---

## Next Steps

1. ✅ Set up Supabase project and tables
2. ✅ Set up Upstash Redis instance
3. ✅ Register for Seoul Open API key
4. ✅ Register Kakao Developer account
5. ✅ Configure all environment variables
6. ✅ Deploy backend to Vercel
7. ✅ Deploy frontend to Vercel
8. ✅ Verify deployment with health checks
9. 🔄 Set up custom domain (optional)
10. 🔄 Enable monitoring and analytics
11. 🔄 Set up CI/CD with GitHub integration

---

## Support

For issues or questions:
- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Kakao Developers**: https://developers.kakao.com/docs
- **Seoul Open Data**: https://data.seoul.go.kr/

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
