# 🚀 Cloud Deployment Guide

This guide will help you deploy your Document Analysis MCP Server to the cloud using MongoDB Atlas and various hosting platforms.

## 📋 Prerequisites

- MongoDB Atlas account (free tier available)
- Google AI API key
- Cloud hosting platform account (Heroku, Railway, DigitalOcean, etc.)

## 🗄️ Step 1: Set up MongoDB Atlas (Free Tier)

### 1.1 Create Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for a free account
3. Create a new project (e.g., "Document Analysis")

### 1.2 Create a Cluster
1. Click "Create a Cluster"
2. Choose **Free Tier (M0)**
3. Select a cloud provider and region (choose closest to your users)
4. Name your cluster (e.g., "document-cluster")
5. Click "Create Cluster" (takes 1-3 minutes)

### 1.3 Configure Database Access
1. Go to **Database Access** in the left sidebar
2. Click **Add New Database User**
3. Choose **Password** authentication
4. Create username and password (save these!)
5. Set privileges to **Read and write to any database**
6. Click **Add User**

### 1.4 Configure Network Access
1. Go to **Network Access** in the left sidebar
2. Click **Add IP Address**
3. For development: Click **Allow Access from Anywhere** (0.0.0.0/0)
4. For production: Add your hosting platform's IP ranges
5. Click **Confirm**

### 1.5 Get Connection String
1. Go to **Database** → **Connect**
2. Choose **Connect your application**
3. Select **Python** and **3.6 or later**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```

## ⚙️ Step 2: Configure Your Application

### 2.1 Update Environment Variables
Edit your `.env` file:

```bash
# MongoDB Atlas Connection String
MONGODB_CONNECTION_STRING=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/document_analysis?retryWrites=true&w=majority

# Google AI API Key
GOOGLE_API_KEY=your-google-ai-api-key

# Database Configuration
DATABASE_NAME=document_analysis
COLLECTION_NAME=document_chunks
VECTOR_INDEX_NAME=vector_index
ENVIRONMENT=production
```

### 2.2 Test Local Connection to Atlas
```bash
python -c "from database.connection import connect_db; from database.models.document_chunk_model import DocumentChunk; import asyncio; asyncio.run(connect_db([DocumentChunk]))"
```

## 🔍 Step 3: Set up Atlas Vector Search (Optional)

For semantic search capabilities:

1. Go to Atlas dashboard → **Search**
2. Click **Create Search Index**
3. Choose **JSON Editor**
4. Use this configuration:

```json
{
  "fields": [
    {
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "text_content",
      "type": "string"
    },
    {
      "path": "document_name", 
      "type": "string"
    }
  ]
}
```

5. Name the index: `vector_index`
6. Click **Create Search Index**

## 🐳 Step 4: Deploy with Docker

### 4.1 Build and Test Locally
```bash
# Build the Docker image
docker build -t mcp-document-server .

# Test locally with Docker
docker-compose up --build
```

### 4.2 Deploy to Cloud Platform

#### Option A: Railway
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Create project: `railway new`
4. Set environment variables in Railway dashboard
5. Deploy: `railway up`

#### Option B: Heroku
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set MONGODB_CONNECTION_STRING="your-atlas-connection-string"
   heroku config:set GOOGLE_API_KEY="your-google-api-key"
   heroku config:set DATABASE_NAME="document_analysis"
   heroku config:set COLLECTION_NAME="document_chunks"
   heroku config:set VECTOR_INDEX_NAME="vector_index"
   heroku config:set ENVIRONMENT="production"
   ```
5. Deploy: `git push heroku main`

#### Option C: DigitalOcean App Platform
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Use the provided Dockerfile
4. Deploy automatically on git push

## ✅ Step 5: Verify Deployment

### 5.1 Test Database Connection
Create a test script to verify your deployment:

```python
# test_cloud_deployment.py
import asyncio
import os
from database.connection import connect_db
from database.models.document_chunk_model import DocumentChunk

async def test_deployment():
    try:
        await connect_db([DocumentChunk])
        print("✅ Cloud database connection successful!")
        
        # Test embedding service
        from services.alternative_embedding_service import AlternativeEmbeddingService
        embedding_service = AlternativeEmbeddingService()
        
        embedding = await embedding_service.get_embedding("Test deployment")
        print(f"✅ Embedding service working! Dimension: {len(embedding)}")
        
        print("🎉 Deployment successful!")
        
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_deployment())
```

### 5.2 Test API Endpoints
Test your deployed application:

```bash
# Test health endpoint (if you have one)
curl https://your-app-url/health

# Test document upload (adjust URL and method as needed)
curl -X POST https://your-app-url/upload \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test.txt", "chunk_size": 1000}'
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Connection Timeout**
   - Check if your IP is whitelisted in Atlas
   - Verify connection string format
   - Check network access rules

2. **Authentication Failed**
   - Verify username/password in connection string
   - Check database user permissions
   - Ensure special characters in password are URL-encoded

3. **SSL/TLS Issues**
   - Ensure `certifi` package is installed
   - Check if TLS is properly configured

4. **Memory Issues**
   - Use smaller chunk sizes for documents
   - Implement proper connection pooling
   - Monitor memory usage on hosting platform

## 📊 Monitoring and Maintenance

1. **Atlas Monitoring**: Use Atlas built-in monitoring for database performance
2. **Application Logs**: Monitor application logs on your hosting platform
3. **Error Tracking**: Consider adding error tracking (Sentry, etc.)
4. **Backup**: Atlas provides automatic backups on free tier

## 🔒 Security Best Practices

1. Use environment variables for all sensitive data
2. Implement proper IP whitelisting
3. Use strong passwords for database users
4. Enable authentication and authorization
5. Regular security updates
6. Monitor access logs

## 💰 Cost Optimization

1. **Atlas Free Tier**: 512MB storage, shared cluster
2. **Monitor Usage**: Check Atlas metrics regularly
3. **Optimize Queries**: Use proper indexing
4. **Connection Pooling**: Reuse connections efficiently

---

🎉 **Your Document Analysis MCP Server is now ready for cloud deployment!**

For additional help, check the troubleshooting section or create an issue in the repository.
