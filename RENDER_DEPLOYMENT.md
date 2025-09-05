# 🚀 Render Deployment Guide

This guide will walk you through deploying your Document Analysis MCP Server to Render.

## Prerequisites

Before deploying, make sure you have:

1. **MongoDB Atlas** account and cluster set up
2. **Google AI API Key** from Google AI Studio
3. **GitHub repository** with your code
4. **Render account** (free tier available)

## Step 1: Prepare Your MongoDB Atlas Database

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a cluster (free M0 tier works fine)
3. Configure database access:
   - Go to Database Access → Add New Database User
   - Create a username and password
   - Set privileges to "Read and write to any database"
4. Configure network access:
   - Go to Network Access → Add IP Address
   - Add `0.0.0.0/0` (allow access from anywhere)
5. Get your connection string:
   - Go to Database → Connect → Connect your application
   - Copy the connection string (it should look like):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

## Step 2: Get Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and save the API key securely

## Step 3: Deploy to Render

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. **Create new service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

3. **Configure the service**:
   - **Name**: `document-analysis-mcp` (or any name you prefer)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. **Set Environment Variables**:
   Click "Advanced" and add these environment variables:
   
   | Key | Value | Description |
   |-----|-------|-------------|
   | `MONGODB_CONNECTION_STRING` | `mongodb+srv://...` | Your MongoDB Atlas connection string |
   | `GOOGLE_API_KEY` | `your-google-ai-key` | Your Google AI API key |
   | `DATABASE_NAME` | `document_analysis` | Database name |
   | `COLLECTION_NAME` | `document_chunks` | Collection name |
   | `VECTOR_INDEX_NAME` | `vector_index` | Vector search index name |
   | `ENVIRONMENT` | `production` | Environment setting |

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)

### Option B: Deploy using Blueprint (render.yaml)

If you want to use the included `render.yaml` blueprint:

1. Go to Render Dashboard → "New +" → "Blueprint"
2. Connect your GitHub repository
3. Select the repository and branch
4. Render will automatically detect the `render.yaml` file
5. Set the environment variables as described above
6. Click "Apply"

## Step 4: Verify Deployment

1. **Check deployment logs**:
   - Go to your service dashboard
   - Check the "Logs" tab for any errors

2. **Test the application**:
   - Once deployed, visit your service URL (provided by Render)
   - You should see the Streamlit interface
   - Try uploading a document and asking questions

3. **Monitor performance**:
   - Check the "Metrics" tab for performance data
   - Monitor memory and CPU usage

## Step 5: Set up MongoDB Vector Search (Optional)

For semantic search functionality:

1. Go to your MongoDB Atlas cluster
2. Navigate to "Search" → "Create Search Index"
3. Choose "JSON Editor" and use this configuration:
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
4. Name the index: `vector_index`
5. Click "Create Search Index"

## Troubleshooting

### Common Issues:

1. **Build fails with dependency errors**:
   - Check that all dependencies in `requirements.txt` are available
   - Try pinning specific versions if needed

2. **Application won't start**:
   - Check logs for error messages
   - Verify environment variables are set correctly
   - Ensure MongoDB connection string is correct

3. **Database connection fails**:
   - Verify MongoDB Atlas network access allows `0.0.0.0/0`
   - Check that username/password in connection string are correct
   - Ensure cluster is not paused

4. **SSL/TLS connection issues**:
   - This is common with MongoDB Atlas
   - The application includes SSL error handling
   - Try redeploying if the issue persists

5. **Memory issues**:
   - Render's free tier has 512MB RAM limit
   - Consider upgrading to a paid plan if needed
   - Optimize chunk sizes for better memory usage

## Performance Optimization

1. **Memory Usage**:
   - Use smaller document chunk sizes (500-1000 tokens)
   - Implement connection pooling
   - Monitor memory usage in Render dashboard

2. **Database Performance**:
   - Create proper indexes in MongoDB
   - Use connection pooling
   - Monitor query performance

3. **Application Performance**:
   - Enable Streamlit caching where appropriate
   - Optimize document processing pipeline
   - Consider using async operations

## Security Best Practices

1. **Environment Variables**:
   - Never commit sensitive data to GitHub
   - Use Render's environment variable management
   - Rotate API keys regularly

2. **Database Security**:
   - Use strong passwords for MongoDB users
   - Regularly review network access rules
   - Monitor access logs

3. **Application Security**:
   - Keep dependencies updated
   - Monitor for security vulnerabilities
   - Implement proper error handling

## Scaling and Monitoring

1. **Scaling**:
   - Monitor resource usage in Render dashboard
   - Upgrade plan if needed
   - Consider horizontal scaling for high traffic

2. **Monitoring**:
   - Use Render's built-in metrics
   - Monitor MongoDB Atlas performance
   - Set up alerts for errors

3. **Backups**:
   - MongoDB Atlas provides automatic backups
   - Consider additional backup strategies for production

## Cost Optimization

1. **Render Free Tier**:
   - 750 hours/month free
   - Sleeps after 15 minutes of inactivity
   - 512MB RAM, shared CPU

2. **MongoDB Atlas Free Tier**:
   - 512MB storage
   - Shared cluster
   - No additional costs

3. **Google AI API**:
   - Pay-per-use pricing
   - Monitor usage to avoid unexpected costs

## Support and Resources

- **Render Documentation**: https://render.com/docs
- **MongoDB Atlas Documentation**: https://docs.atlas.mongodb.com
- **Google AI Documentation**: https://ai.google.dev/docs

Your Document Analysis MCP Server is now ready for production use on Render! 🎉
