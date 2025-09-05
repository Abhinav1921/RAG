# 🚂 Deploy to Railway

## Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version
```

## Step 2: Initialize and Deploy

```bash
# Login to Railway (opens browser)
railway login

# Initialize Railway project
railway new

# Deploy your project
railway up

# Add environment variables
railway variables set MONGODB_CONNECTION_STRING="mongodb+srv://agrawalabhinav38_db_user:Abhi_1921@cluster1.bj9yesu.mongodb.net/document_analysis?retryWrites=true&w=majority&appName=Cluster1"
railway variables set GOOGLE_API_KEY="AIzaSyBvQIapso5qR59LGzwQBXf_mvyFPQpVV2o"
railway variables set DATABASE_NAME="document_analysis"
railway variables set COLLECTION_NAME="document_chunks"
railway variables set VECTOR_INDEX_NAME="vector_index"
railway variables set ENVIRONMENT="production"

# Get your public URL
railway domain
```

## Step 3: Configure for Web App

Your app will be available at: `https://your-app-name.up.railway.app`

## Automatic Deployment

Once set up, Railway automatically redeploys on every git push to your main branch!
