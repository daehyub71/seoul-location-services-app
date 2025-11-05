# Vercel Deployment Guide

Complete step-by-step guide for deploying Seoul Location Services to Vercel.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Post-Deployment Configuration](#post-deployment-configuration)
6. [Verification](#verification)
7. [CI/CD Setup](#cicd-setup)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

1. **Vercel Account**: Sign up at https://vercel.com
2. **Supabase Account**: Sign up at https://supabase.com
3. **Upstash Account**: Sign up at https://upstash.com
4. **Kakao Developers Account**: Sign up at https://developers.kakao.com
5. **Seoul Open Data Account**: Sign up at https://data.seoul.go.kr

### Required Tools

```bash
# Install Node.js (v18 or higher)
node --version  # Check version

# Install Vercel CLI
npm install -g vercel

# Verify installation
vercel --version
```

### GitHub Repository

Ensure your code is pushed to GitHub:
```bash
git remote -v
git push origin main
```

---

## Project Structure

```
seoul-location-services-app/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── vercel.json          ✅ Created
│   └── .env.example
├── backend/
│   ├── app/
│   ├── api/
│   │   └── index.py         ✅ Created (Vercel handler)
│   ├── requirements.txt
│   ├── vercel.json          ✅ Created
│   └── .env.example
├── VERCEL_ENV_VARIABLES.md   ✅ Created
└── VERCEL_DEPLOYMENT_GUIDE.md ✅ This file
```

---

## Backend Deployment

### Step 1: Prepare Backend

```bash
# Navigate to backend directory
cd backend

# Verify vercel.json exists
cat vercel.json

# Verify api/index.py exists
cat api/index.py
```

### Step 2: Login to Vercel

```bash
# Login to Vercel
vercel login

# Select your preferred authentication method:
# - GitHub
# - GitLab
# - Bitbucket
# - Email
```

### Step 3: Deploy Backend (First Time)

```bash
# Initialize Vercel project
vercel

# Follow the prompts:
```

**Prompts and Answers:**

```
? Set up and deploy "~/seoul-location-services-app/backend"? [Y/n]
→ Y

? Which scope do you want to deploy to?
→ (Select your Vercel account)

? Link to existing project? [y/N]
→ N

? What's your project's name?
→ seoul-location-services-backend

? In which directory is your code located?
→ ./

? Want to override the settings? [y/N]
→ N
```

**Expected Output:**

```
🔗  Linked to your-account/seoul-location-services-backend
🔍  Inspect: https://vercel.com/your-account/seoul-location-services-backend/[deployment-id]
✅  Preview: https://seoul-location-services-backend-[hash].vercel.app
```

### Step 4: Configure Backend Environment Variables

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select project: **seoul-location-services-backend**
3. Go to: **Settings** → **Environment Variables**
4. Add all required variables from [VERCEL_ENV_VARIABLES.md](./VERCEL_ENV_VARIABLES.md)

**Critical Variables** (must be set):

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres.xxx:password@...

# Redis
UPSTASH_URL=https://xxx.upstash.io
UPSTASH_TOKEN=AbCdEfGhIjKlMnOpQrStUvWxYz...
REDIS_URL=https://xxx.upstash.io

# APIs
SEOUL_API_KEY=your_seoul_api_key
KAKAO_REST_API_KEY=your_kakao_rest_api_key

# Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_ENABLED=true
COLLECTION_SCHEDULE_ENABLED=false  # ⚠️ Disable for serverless
```

**Important**: Set environment for **Production**, **Preview**, and **Development**

### Step 5: Deploy to Production

```bash
# Deploy to production
vercel --prod

# Expected output:
✅  Production: https://seoul-location-services-backend.vercel.app
```

### Step 6: Verify Backend Deployment

```bash
# Test health endpoint
curl https://your-backend.vercel.app/health

# Expected response:
{
  "status": "healthy",
  "version": "v1",
  "environment": "production",
  "cache_enabled": true
}

# Test API docs
open https://your-backend.vercel.app/docs
```

---

## Frontend Deployment

### Step 1: Prepare Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Verify vercel.json exists
cat vercel.json

# Build test (optional)
npm install
npm run build
```

### Step 2: Deploy Frontend (First Time)

```bash
# Initialize Vercel project
vercel

# Follow the prompts:
```

**Prompts and Answers:**

```
? Set up and deploy "~/seoul-location-services-app/frontend"? [Y/n]
→ Y

? Which scope do you want to deploy to?
→ (Select your Vercel account)

? Link to existing project? [y/N]
→ N

? What's your project's name?
→ seoul-location-services-frontend

? In which directory is your code located?
→ ./

? Want to override the settings? [y/N]
→ N
```

### Step 3: Configure Frontend Environment Variables

1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Select project: **seoul-location-services-frontend**
3. Go to: **Settings** → **Environment Variables**
4. Add required variables:

**Critical Variables**:

```bash
# Backend API URL (from backend deployment)
VITE_API_BASE_URL=https://seoul-location-services-backend.vercel.app

# Kakao JavaScript Key (NOT REST API Key!)
VITE_KAKAO_MAP_API_KEY=your_kakao_javascript_key

# App Configuration (optional)
VITE_APP_NAME=Seoul Location Services
VITE_APP_VERSION=1.0.0
VITE_DEFAULT_LAT=37.5665
VITE_DEFAULT_LON=126.9780
VITE_DEFAULT_ZOOM=5
VITE_ENABLE_DARK_MODE=false
VITE_ENABLE_LLM_RECOMMENDATIONS=false
VITE_ENABLE_ANALYTICS=false
```

### Step 4: Configure Kakao JavaScript Key

1. Go to [Kakao Developers Console](https://developers.kakao.com/console/app)
2. Select your application
3. Go to: **App Settings** → **Platform** → **Web**
4. Click **Add Platform** → Select **Web**
5. Add domains:
   - `https://seoul-location-services-frontend.vercel.app`
   - `https://*.vercel.app` (for preview deployments)
   - `http://localhost:5173` (for local development)
6. Click **Save**
7. Copy the **JavaScript Key** (found in Summary page)
8. Wait 5-10 minutes for DNS propagation

### Step 5: Deploy to Production

```bash
# Deploy to production
vercel --prod

# Expected output:
✅  Production: https://seoul-location-services-frontend.vercel.app
```

### Step 6: Verify Frontend Deployment

1. Open: https://your-frontend.vercel.app
2. Check:
   - ✅ Map loads with Kakao Map visualization
   - ✅ Location services display on map
   - ✅ Service list shows data
   - ✅ Clicking markers shows InfoWindow with all data
   - ✅ No CORS errors in browser console

---

## Post-Deployment Configuration

### 1. Update Backend CORS (if needed)

If using custom domain, add to backend environment:

```bash
# In Vercel Dashboard → Backend Project → Settings → Environment Variables
CORS_ORIGINS_EXTRA=https://myapp.com,https://www.myapp.com
```

### 2. Set Up Custom Domain (Optional)

**Frontend:**
1. Go to: Frontend Project → **Settings** → **Domains**
2. Click **Add Domain**
3. Enter: `myapp.com`
4. Follow DNS configuration instructions
5. Vercel automatically provisions SSL certificate

**Backend:**
1. Go to: Backend Project → **Settings** → **Domains**
2. Click **Add Domain**
3. Enter: `api.myapp.com`
4. Follow DNS configuration instructions

**Update Frontend Environment:**
```bash
VITE_API_BASE_URL=https://api.myapp.com
```

### 3. Enable Vercel Analytics (Optional)

1. Go to: Frontend Project → **Analytics**
2. Click **Enable Analytics**
3. View real-time traffic and Web Vitals

### 4. Enable Password Protection for Preview (Optional)

1. Go to: Project → **Settings** → **General**
2. Scroll to: **Deployment Protection**
3. Enable: **Password Protection**
4. Set password for preview deployments

---

## CI/CD Setup

### Automatic Deployment with Git Integration

Vercel automatically deploys when you push to GitHub:

**Production Deployments:**
```bash
git push origin main  # Deploys to production
```

**Preview Deployments:**
```bash
git push origin feature-branch  # Creates preview deployment
```

### Configure Git Integration

1. Go to: Project → **Settings** → **Git**
2. Connect GitHub repository
3. Configure:
   - **Production Branch**: `main`
   - **Preview Branches**: All branches
   - **Auto-deploy**: Enabled

### Environment Branches

Configure different environments:

1. Go to: **Settings** → **Environment Variables**
2. Set different values for:
   - **Production**: Main branch
   - **Preview**: Feature branches
   - **Development**: Local development

---

## Verification Checklist

### Backend Health Checks

- [ ] Health endpoint responds: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Sample API call works: `/api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000`
- [ ] Redis cache working (check response times)
- [ ] Database connection successful
- [ ] No errors in function logs

### Frontend Health Checks

- [ ] Homepage loads successfully
- [ ] Kakao Map displays correctly
- [ ] Markers appear on map
- [ ] InfoWindow displays all data
- [ ] Service list loads data
- [ ] Clicking service items shows InfoWindow
- [ ] No CORS errors in console
- [ ] No JavaScript errors in console

### Integration Tests

```bash
# Test nearby services API
curl "https://your-backend.vercel.app/api/v1/services/nearby?lat=37.5665&lon=126.9780&radius=2000"

# Expected: JSON response with services array

# Test frontend-backend integration
open https://your-frontend.vercel.app
# Click on map → Verify markers load
# Click marker → Verify InfoWindow appears
# Click service list item → Verify InfoWindow appears
```

---

## Troubleshooting

### Common Backend Issues

#### Issue: 500 Internal Server Error

**Symptoms:**
- Backend returns 500 errors
- Function logs show missing environment variables

**Solution:**
```bash
# Check environment variables in Vercel Dashboard
# Verify all required variables are set
# Redeploy: vercel --prod
```

#### Issue: Database Connection Timeout

**Symptoms:**
- Timeout errors in function logs
- "could not connect to server" errors

**Solution:**
```bash
# 1. Check SUPABASE_DATABASE_URL uses Session mode (port 6543)
# Correct: postgresql://postgres.xxx:password@...pooler.supabase.com:6543/postgres
# Wrong:   postgresql://postgres.xxx:password@...pooler.supabase.com:5432/postgres

# 2. Verify connection string in Supabase Dashboard
# Settings → Database → Connection string → Session mode

# 3. Test connection in Vercel function logs
```

#### Issue: Redis Connection Failed

**Symptoms:**
- Cache not working
- "UPSTASH_URL not set" errors

**Solution:**
```bash
# 1. Verify UPSTASH_URL is HTTPS REST endpoint
# Correct: https://xxx-xxx.upstash.io
# Wrong:   redis://xxx-xxx.upstash.io:6379

# 2. Check UPSTASH_TOKEN is correct
# Get from: Upstash Console → Database → REST API → Token

# 3. Verify REDIS_URL = UPSTASH_URL
```

#### Issue: CORS Errors

**Symptoms:**
- Browser console shows CORS policy errors
- Frontend cannot call backend API

**Solution:**
```bash
# 1. Check backend CORS configuration includes frontend domain
# Backend code already includes: https://*.vercel.app

# 2. For custom domains, add to backend environment:
CORS_ORIGINS_EXTRA=https://myapp.com

# 3. Redeploy backend: vercel --prod

# 4. Clear browser cache and test again
```

### Common Frontend Issues

#### Issue: Map Not Loading

**Symptoms:**
- Blank map area
- Console error: "kakao is not defined"

**Solution:**
```bash
# 1. Verify VITE_KAKAO_MAP_API_KEY is set
# 2. Ensure it's the JavaScript Key (NOT REST API Key)
# 3. Check domain is registered in Kakao Developer Console:
#    - Settings → Platform → Web → Add your Vercel domain
# 4. Wait 5-10 minutes after adding domain
# 5. Clear browser cache and reload
```

#### Issue: Backend API Not Responding

**Symptoms:**
- Services don't load
- Console error: "Failed to fetch"

**Solution:**
```bash
# 1. Check VITE_API_BASE_URL is correct
# Should be: https://your-backend.vercel.app (no trailing slash)

# 2. Verify backend is deployed and healthy:
curl https://your-backend.vercel.app/health

# 3. Check backend CORS allows frontend domain
# 4. Redeploy frontend after changing env variables
```

#### Issue: InfoWindow Not Showing Data

**Symptoms:**
- InfoWindow appears but shows incomplete data
- Console errors about undefined properties

**Solution:**
```bash
# 1. Check browser console for specific errors
# 2. Verify backend API response includes all fields
# 3. Check kakao.ts createServiceInfoWindowContent() function
# 4. Clear browser cache and test again
```

### Vercel Platform Issues

#### Issue: Build Failed

**Symptoms:**
- Deployment fails with build errors
- Red X in deployments list

**Solution:**
```bash
# 1. Check build logs in Vercel Dashboard
#    Deployments → Select failed deployment → View logs

# 2. Common causes:
#    - Missing dependencies in package.json
#    - TypeScript errors
#    - Environment variables not set for build

# 3. Test build locally:
npm run build

# 4. Fix errors and redeploy
```

#### Issue: Function Timeout

**Symptoms:**
- 504 Gateway Timeout errors
- "FUNCTION_INVOCATION_TIMEOUT" in logs

**Solution:**
```bash
# 1. Optimize database queries
# 2. Add Redis caching
# 3. Upgrade Vercel plan for 60s timeout (Hobby: 10s, Pro: 60s)
# 4. Check vercel.json maxDuration setting
```

---

## Monitoring and Maintenance

### View Function Logs

```bash
# In Vercel Dashboard:
1. Go to: Deployments
2. Click on deployment
3. Click: **View Function Logs**
4. Monitor real-time logs
```

### Monitor Performance

```bash
# In Vercel Dashboard:
1. Go to: Analytics
2. View metrics:
   - Response time
   - Error rate
   - Requests per second
   - Web Vitals (LCP, FID, CLS)
```

### Update Deployment

```bash
# Method 1: Git push (recommended)
git add .
git commit -m "feat: update feature"
git push origin main

# Method 2: Manual deployment
cd frontend  # or backend
vercel --prod
```

### Rollback Deployment

```bash
# In Vercel Dashboard:
1. Go to: Deployments
2. Find previous working deployment
3. Click: **⋯** → **Promote to Production**
```

---

## Performance Optimization

### Backend Optimization

1. **Enable Redis Caching**
   ```bash
   CACHE_ENABLED=true
   REDIS_CACHE_TTL=300  # 5 minutes
   ```

2. **Optimize Database Queries**
   - Add indexes to frequently queried columns
   - Use Supabase query optimization

3. **Reduce Function Cold Starts**
   - Minimize dependencies in requirements.txt
   - Keep lambda size < 50MB

### Frontend Optimization

1. **Enable Vite Build Optimizations**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     build: {
       minify: 'terser',
       sourcemap: false,
       rollupOptions: {
         output: {
           manualChunks: {
             'react-vendor': ['react', 'react-dom'],
             'map-vendor': ['@/services/kakao'],
           }
         }
       }
     }
   })
   ```

2. **Enable Vercel Image Optimization**
   - Use `<Image>` component from next/image
   - Optimize images before deployment

3. **Enable Caching Headers**
   - Already configured in vercel.json
   - Assets cached for 1 year

---

## Cost Optimization

### Vercel Free Tier Limits

- **Function Execution**: 100 GB-hours/month
- **Bandwidth**: 100 GB/month
- **Builds**: Unlimited
- **Deployments**: Unlimited

### Tips to Stay Within Free Tier

1. **Enable Redis caching** to reduce function invocations
2. **Optimize images** to reduce bandwidth
3. **Minimize API calls** with smart caching
4. **Use Supabase free tier** (500 MB storage)
5. **Use Upstash free tier** (10K commands/day)

### Upgrade Considerations

Upgrade to Pro ($20/month) if:
- Need > 10s function timeout
- Exceed bandwidth limits
- Need password protection
- Need advanced analytics
- Need team collaboration

---

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use Vercel's encrypted storage
   - Rotate keys regularly

2. **API Keys**
   - Keep service_role keys secret
   - Use CORS to restrict domains
   - Monitor API usage

3. **Database Security**
   - Enable Supabase Row Level Security (RLS)
   - Use prepared statements
   - Audit access logs

4. **Frontend Security**
   - Enable CSP headers (Content Security Policy)
   - Validate all user inputs
   - Sanitize displayed data

5. **Monitoring**
   - Set up Sentry for error tracking
   - Monitor function logs
   - Set up alerts for anomalies

---

## Next Steps

After successful deployment:

1. ✅ Set up custom domain
2. ✅ Enable Vercel Analytics
3. ✅ Configure Sentry error tracking
4. ✅ Set up monitoring alerts
5. ✅ Create deployment documentation for team
6. ✅ Configure CI/CD pipeline
7. ✅ Set up staging environment
8. ✅ Create backup strategy
9. ✅ Plan scaling strategy
10. ✅ Schedule maintenance windows

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Supabase Docs**: https://supabase.com/docs
- **Kakao Developers**: https://developers.kakao.com/docs
- **Community**: Vercel Discord, Supabase Discord

---

## Deployment Checklist

### Pre-Deployment

- [ ] All code committed to Git
- [ ] Tests passing locally
- [ ] Build successful locally
- [ ] Environment variables documented
- [ ] API keys obtained
- [ ] Database schema migrated

### Deployment

- [ ] Backend deployed to Vercel
- [ ] Backend environment variables configured
- [ ] Backend health check passing
- [ ] Frontend deployed to Vercel
- [ ] Frontend environment variables configured
- [ ] Frontend loads successfully

### Post-Deployment

- [ ] Integration tests passing
- [ ] No errors in function logs
- [ ] No errors in browser console
- [ ] Performance acceptable
- [ ] Analytics enabled
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team notified

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
**Maintained by**: Seoul Location Services Team

---

## Quick Reference Commands

```bash
# Login
vercel login

# Deploy preview
vercel

# Deploy production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Remove deployment
vercel rm [deployment-url]

# Link project
vercel link

# Pull environment variables
vercel env pull

# View project info
vercel inspect
```
