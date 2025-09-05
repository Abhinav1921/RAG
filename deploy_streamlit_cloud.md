# ☁️ Deploy to Streamlit Community Cloud

## Perfect for Your Streamlit App!

### Step 1: Prepare Your Repository

1. **Push to GitHub**: Make sure your code is in a public GitHub repository
2. **Add secrets management** (create this file):

```toml
# .streamlit/secrets.toml
[secrets]
MONGODB_CONNECTION_STRING = "mongodb+srv://agrawalabhinav38_db_user:Abhi_1921@cluster1.bj9yesu.mongodb.net/document_analysis?retryWrites=true&w=majority&appName=Cluster1"
GOOGLE_API_KEY = "AIzaSyBvQIapso5qR59LGzwQBXf_mvyFPQpVV2o"
DATABASE_NAME = "document_analysis"
COLLECTION_NAME = "document_chunks"
VECTOR_INDEX_NAME = "vector_index"
ENVIRONMENT = "production"
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Select your repository**: `your-username/poc_mcp`
5. **Main file path**: `document_streamlit_app.py`
6. **Click "Deploy!"**

### Step 3: Add Secrets (Important!)

1. **In Streamlit Cloud dashboard**, click on your app
2. **Go to Settings → Secrets**
3. **Copy-paste the contents** from `.streamlit/secrets.toml`
4. **Click "Save"**

### Step 4: Access Your App

Your app will be available at:
`https://your-username-poc-mcp-document-streamlit-app-abcdef.streamlit.app/`

## 🔒 Security Note

Add `.streamlit/secrets.toml` to your `.gitignore` file so secrets aren't committed to GitHub:

```bash
echo ".streamlit/secrets.toml" >> .gitignore
```
