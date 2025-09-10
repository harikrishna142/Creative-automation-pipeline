# AWS S3 Setup Guide

## 🔧 How to Get AWS Credentials

### Step 1: Create an AWS Account
1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Sign up for a free AWS account if you don't have one
3. Complete the account verification process

### Step 2: Create an S3 Bucket
1. Log into AWS Console
2. Go to **S3** service
3. Click **"Create bucket"**
4. Choose a unique bucket name (e.g., `your-name-creative-automation-pipeline`)
5. Select a region (e.g., `us-east-1`)
6. Keep default settings for now
7. Click **"Create bucket"**

### Step 3: Create IAM User for Programmatic Access
1. Go to **IAM** service in AWS Console
2. Click **"Users"** in the left sidebar
3. Click **"Create user"**
4. Enter username: `creative-automation-user`
5. Select **"Programmatic access"**
6. Click **"Next: Permissions"**

### Step 4: Attach S3 Policy
1. Click **"Attach existing policies directly"**
2. Search for and select: **"AmazonS3FullAccess"**
3. Click **"Next: Tags"** (optional)
4. Click **"Next: Review"**
5. Click **"Create user"**

### Step 5: Get Access Keys
1. After user creation, you'll see the **Access Key ID** and **Secret Access Key**
2. **IMPORTANT**: Download the CSV file or copy these credentials immediately
3. You won't be able to see the secret key again!

## 🔐 Setting Up Environment Variables

### Option 1: Create .env File (Recommended)
Create a file named `.env` in your project root with this content:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google AI Configuration (for Veo 3)
GOOGLE_API_KEY=your_google_api_key_here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIA...your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name-here

# Optional: Custom S3 Configuration
S3_PREFIX=campaigns
S3_REGION=us-east-1

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
```

### Option 2: Set Environment Variables in Windows
Open PowerShell as Administrator and run:

```powershell
# Set AWS credentials
$env:AWS_ACCESS_KEY_ID="AKIA...your_access_key_id_here"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key_here"
$env:AWS_DEFAULT_REGION="us-east-1"
$env:S3_BUCKET_NAME="your-bucket-name-here"

# Set OpenAI API key
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### Option 3: Set Environment Variables Permanently
1. Open **System Properties** → **Environment Variables**
2. Add new user variables:
   - `AWS_ACCESS_KEY_ID` = your access key
   - `AWS_SECRET_ACCESS_KEY` = your secret key
   - `AWS_DEFAULT_REGION` = us-east-1
   - `S3_BUCKET_NAME` = your bucket name
   - `OPENAI_API_KEY` = your OpenAI API key

## 🧪 Testing Your Setup

### Test S3 Connection
Run this Python script to test your S3 connection:

```python
import boto3
import os

# Test S3 connection
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    )
    
    # List buckets to test connection
    response = s3_client.list_buckets()
    print("✅ S3 connection successful!")
    print(f"Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
    
except Exception as e:
    print(f"❌ S3 connection failed: {e}")
```

## 🔒 Security Best Practices

1. **Never commit credentials to Git**: Add `.env` to your `.gitignore` file
2. **Use IAM roles in production**: For production, use IAM roles instead of access keys
3. **Rotate keys regularly**: Change your access keys periodically
4. **Limit permissions**: Only grant the minimum required permissions
5. **Use different keys for different environments**: Separate dev/staging/prod credentials

## 🆘 Troubleshooting

### Common Issues:
1. **"Access Denied"**: Check if your IAM user has S3 permissions
2. **"Bucket not found"**: Verify the bucket name and region
3. **"Invalid credentials"**: Double-check your access key and secret key
4. **"Region mismatch"**: Ensure the region in your code matches the bucket region

### Getting Help:
- AWS Documentation: https://docs.aws.amazon.com/s3/
- IAM Documentation: https://docs.aws.amazon.com/iam/
- AWS Support: Available in AWS Console

## 📝 Example .env File

Here's a complete example (replace with your actual values):

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123...your_actual_key

# Google AI Configuration (for Veo 3)
GOOGLE_API_KEY=AIza...your_google_key

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=my-creative-automation-bucket

# Optional: Custom S3 Configuration
S3_PREFIX=campaigns
S3_REGION=us-east-1

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
```

Once you've set up your credentials, restart the Streamlit app and the S3 storage should work!
