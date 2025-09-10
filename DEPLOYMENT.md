# 🚀 Deployment Guide - PlayTheList

This guide covers deploying PlayTheList securely for public access.

## 🔐 Security Features Implemented

✅ **Rate Limiting**: 3 transfers per hour per user  
✅ **Input Validation**: URL sanitization and validation  
✅ **Error Handling**: Comprehensive error logging  
✅ **Environment Security**: Secure API key management  
✅ **Logging**: Application activity tracking  

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended for MVP)

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in the Streamlit Cloud dashboard:
   ```
   SPOTIFY_CLIENT_ID = your_actual_client_id
   SPOTIFY_CLIENT_SECRET = your_actual_client_secret
   SPOTIFY_REDIRECT_URI = https://your-app.streamlit.app/callback
   OPENAI_API_KEY = your_actual_openai_key
   ```
5. Deploy!

**Pros:**
- Free hosting
- Automatic HTTPS
- Built-in secret management
- Easy updates

**Cons:**
- Limited customization
- Shared resources

### Option 2: Docker + Cloud Provider

**For Google Cloud Run:**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/playthelist

# Deploy to Cloud Run
gcloud run deploy playthelist \
  --image gcr.io/PROJECT_ID/playthelist \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SPOTIFY_CLIENT_ID=your_id,SPOTIFY_CLIENT_SECRET=your_secret
```

**For AWS ECS:**
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t playthelist .
docker tag playthelist:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/playthelist:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/playthelist:latest
```

### Option 3: Railway/Render

**Railway:**
1. Connect GitHub repository
2. Add environment variables in dashboard
3. Deploy automatically

**Render:**
1. Create new Web Service
2. Connect GitHub repository
3. Add environment variables
4. Deploy

## 🔧 Environment Variables

Required for all deployments:

```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://your-domain.com/callback
OPENAI_API_KEY=your_openai_api_key
```

## 🛡️ Security Checklist

- [ ] API keys stored securely (not in code)
- [ ] Rate limiting enabled
- [ ] Input validation active
- [ ] Error logging configured
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] No sensitive data in logs

## 📊 Monitoring

The app includes logging to `app.log`. For production:

1. **Set up log aggregation** (e.g., Google Cloud Logging, AWS CloudWatch)
2. **Monitor API usage** to prevent quota exhaustion
3. **Set up alerts** for errors and rate limit violations
4. **Track user metrics** for capacity planning

## 🚨 Troubleshooting

**Common Issues:**

1. **"Missing environment variables"**
   - Check that all required variables are set
   - Verify variable names match exactly

2. **"Rate limit exceeded"**
   - Normal behavior for security
   - Users can wait or contact for higher limits

3. **"Transfer failed"**
   - Check API quotas
   - Verify playlist URLs are public
   - Check logs for specific errors

## 🔄 Updates

To update the deployed app:
1. Push changes to GitHub
2. Streamlit Cloud: Auto-deploys
3. Docker: Rebuild and redeploy
4. Other platforms: Follow their update process

## 📈 Scaling

For higher traffic:
1. **Increase rate limits** in code
2. **Add Redis** for distributed rate limiting
3. **Use load balancer** for multiple instances
4. **Implement caching** for repeated requests
5. **Add user authentication** for premium features

## 💰 Cost Management

- **Monitor API usage** (OpenAI, Spotify)
- **Set up billing alerts**
- **Consider caching** to reduce API calls
- **Implement usage tiers** for different user types
