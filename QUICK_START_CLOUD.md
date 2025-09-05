# 🚀 Quick Start: Cloud Deployment

Get your Document Analysis MCP Server running in the cloud in under 30 minutes!

## ⚡ 5-Minute Setup

### 1. Set up MongoDB Atlas (FREE)

1. **Create Account**: Go to [MongoDB Atlas](https://www.mongodb.com/atlas) and sign up
2. **Create Cluster**: Choose **Free Tier (M0)** - No credit card required
3. **Database User**: Create username/password (remember these!)
4. **Network Access**: Click "Allow Access from Anywhere" for now
5. **Connection String**: Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```

### 2. Update Your .env File

```bash
# Replace these values with your actual Atlas credentials
MONGODB_CONNECTION_STRING=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/document_analysis?retryWrites=true&w=majority
GOOGLE_API_KEY=your-existing-google-api-key
DATABASE_NAME=document_analysis
COLLECTION_NAME=document_chunks
VECTOR_INDEX_NAME=vector_index
ENVIRONMENT=production
```

### 3. Test Your Setup

```bash
# Install missing dependency
pip install certifi

# Test the cloud configuration
python test_cloud_deployment.py
```

### 4. Deploy to Cloud Platform

Choose your preferred platform:

#### Option A: Railway (Recommended - Free tier)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy (will prompt for login)
railway login
railway new
railway up
```

#### Option B: Heroku
```bash
# Install Heroku CLI, then:
heroku create your-app-name
git push heroku main
```

#### Option C: DigitalOcean App Platform
- Connect your GitHub repository
- Set environment variables in dashboard
- Deploy automatically

## 🔍 Testing Your Deployment

Once deployed, test your endpoints:

```bash
# Replace YOUR_APP_URL with your actual deployment URL
curl https://YOUR_APP_URL/health

# Test Streamlit app (if deployed)
# Visit: https://YOUR_APP_URL:8501
```

## ⚠️ Common Issues & Quick Fixes

### Database Connection Issues
```bash
# Check your connection string format
# Should look like: mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Common mistakes:
# ❌ mongodb://localhost:27017/database  (local, not cloud)
# ❌ Missing password or special characters not encoded
# ✅ mongodb+srv://user:pass123@cluster0.abc123.mongodb.net/document_analysis?retryWrites=true&w=majority
```

### IP Whitelist Issues
1. Go to Atlas → Network Access
2. Click "Add IP Address" 
3. Choose "Allow Access from Anywhere" (0.0.0.0/0)

### Environment Variable Issues
Make sure your hosting platform has these set:
- `MONGODB_CONNECTION_STRING`
- `GOOGLE_API_KEY`
- `DATABASE_NAME`
- `COLLECTION_NAME` 
- `VECTOR_INDEX_NAME`
- `ENVIRONMENT=production`

## 🎯 Next Steps After Deployment

1. **Set up Vector Search** (optional but recommended):
   - Run: `python setup_vector_search.py`
   - Follow the Atlas UI instructions

2. **Upload Test Documents**:
   - Use the Streamlit app interface
   - Or call the API endpoints directly

3. **Monitor Performance**:
   - Check Atlas dashboard for database metrics
   - Monitor your hosting platform logs

## 💡 Pro Tips

- **Free Tiers**: Both Atlas (512MB) and Railway/Heroku have generous free tiers
- **Scaling**: Start with free tier, upgrade as needed
- **Security**: Use environment variables, never hardcode secrets
- **Backups**: Atlas provides automatic backups on free tier

## 🆘 Need Help?

1. **Connection Issues**: Check the DEPLOYMENT_GUIDE.md troubleshooting section
2. **API Issues**: Verify your Google AI API key has quota
3. **Deployment Issues**: Check your platform's logs and documentation

---

🎉 **That's it! Your Document Analysis MCP Server should now be running in the cloud!**

Visit your deployed URL and start uploading documents for AI-powered analysis.
