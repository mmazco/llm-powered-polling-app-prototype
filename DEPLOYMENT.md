# 🚀 Deployment Guide

## LLM-Powered Polling App Prototype Deployment

This guide provides instructions for deploying the LLM-powered polling app prototype to production environments.

## 📋 Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- OpenAI API Key
- Git repository access

## 🌐 Frontend Deployment (Vercel/Netlify)

### Vercel Deployment (Recommended)

1. **Connect Repository**
   ```bash
   # Push your code to GitHub first
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure build settings:
     - Framework Preset: `Next.js`
     - Build Command: `npm run build`
     - Output Directory: `.next`
     - Install Command: `npm install`

3. **Environment Variables (Frontend)**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

### Netlify Deployment

1. **Build Settings**
   - Build Command: `npm run build`
   - Publish Directory: `out`
   - Add to `next.config.js`:
     ```javascript
     const nextConfig = {
       output: 'export',
       trailingSlash: true,
       images: { unoptimized: true }
     }
     ```

## 🖥️ Backend Deployment

### Railway Deployment (Recommended)

1. **Prepare for Deployment**
   ```bash
   # Create Procfile in backend directory
   echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile
   ```

2. **Deploy to Railway**
   - Visit [railway.app](https://railway.app)
   - Connect GitHub repository
   - Select `backend` folder as root
   - Set environment variables:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     PORT=8001
     ENVIRONMENT=production
     CORS_ORIGINS=https://your-frontend-url.vercel.app
     ```

### Docker Deployment

1. **Create Dockerfile** (in backend directory)
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8001

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
   ```

2. **Build and Deploy**
   ```bash
   docker build -t llm-polling-backend ./backend
   docker run -p 8001:8001 --env-file .env llm-polling-backend
   ```

### Heroku Deployment

1. **Prepare Backend**
   ```bash
   # Add to backend/requirements.txt
   gunicorn==21.2.0
   
   # Create backend/Procfile
   echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name-backend
   heroku config:set OPENAI_API_KEY=your_key_here
   git subtree push --prefix backend heroku main
   ```

## 🔧 Production Configuration

### Environment Variables

**Backend (.env)**
```bash
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=production
PORT=8001
HOST=0.0.0.0
CORS_ORIGINS=https://your-frontend-domain.com
```

**Frontend**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Configure proper CORS origins for production
3. **HTTPS**: Ensure both frontend and backend use HTTPS
4. **Rate Limiting**: Consider adding rate limiting to backend API

## 📊 Monitoring & Analytics

### Error Tracking
- **Frontend**: Integrate Sentry or LogRocket
- **Backend**: Use structured logging with tools like DataDog

### Performance Monitoring
- **Frontend**: Vercel Analytics or Google Analytics
- **Backend**: APM tools like New Relic or DataDog

## 🔄 CI/CD Setup

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: '18'
    - run: npm ci
    - run: npm run build
    
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: cd backend && pip install -r requirements.txt
    - run: cd backend && python -m pytest  # if you have tests
```

## 🧪 Testing Before Deployment

```bash
# Frontend
npm run build
npm run start

# Backend
cd backend
python -m pytest  # if you have tests
uvicorn main:app --reload

# Full E2E Test
curl -X POST "https://your-backend-url.up.railway.app/generate-topic" \
  -H "Content-Type: application/json" \
  -d '{"community_context": {"location": "Test City", "population_size": 50000}}'
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ORIGINS environment variable
2. **API Connection Failed**: Verify backend URL in frontend env
3. **OpenAI API Errors**: Check API key and rate limits
4. **Build Failures**: Ensure all dependencies in package.json

### Health Checks

- Frontend: `https://your-app.vercel.app/`
- Backend: `https://your-backend.railway.app/health`

## 📱 Mobile Optimization

The app is mobile-first by design, but test on:
- iOS Safari
- Android Chrome
- Various screen sizes

## 🔐 Security Checklist

- [ ] OpenAI API key secured in environment variables
- [ ] CORS properly configured
- [ ] HTTPS enabled on both frontend and backend
- [ ] No sensitive data in client-side code
- [ ] Input validation on all API endpoints
- [ ] Rate limiting configured

---

**Ready for Production!** 🎉

Your LLM-powered polling app prototype is now ready for the world to experience democratic participation through AI-powered community polling. 