#!/usr/bin/env python3
"""
Test script to verify AWS S3 credentials and configuration.
Run this script to check if your AWS setup is working correctly.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

def test_environment_variables():
    """Test if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION',
        'S3_BUCKET_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set!")
    return True

def test_boto3_import():
    """Test if boto3 is installed and can be imported."""
    print("\n🔍 Testing boto3 import...")
    try:
        import boto3
        print("✅ boto3 imported successfully")
        return True
    except ImportError as e:
        print(f"❌ boto3 import failed: {e}")
        print("💡 Install boto3 with: pip install boto3")
        return False

def test_s3_connection():
    """Test S3 connection with provided credentials."""
    print("\n🔍 Testing S3 connection...")
    try:
        import boto3
        
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        )
        
        # Test connection by listing buckets
        response = s3_client.list_buckets()
        print("✅ S3 connection successful!")
        print(f"📁 Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
        
        # Check if our target bucket exists
        bucket_name = os.getenv('S3_BUCKET_NAME')
        bucket_exists = any(bucket['Name'] == bucket_name for bucket in response['Buckets'])
        
        if bucket_exists:
            print(f"✅ Target bucket '{bucket_name}' exists!")
        else:
            print(f"⚠️  Target bucket '{bucket_name}' not found in your account")
            print("💡 Create the bucket in AWS Console or update S3_BUCKET_NAME")
        
        return True
        
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

def test_s3_storage_manager():
    """Test our S3StorageManager class."""
    print("\n🔍 Testing S3StorageManager...")
    try:
        from pipeline.config import load_config, validate_config
        from pipeline.s3_storage import S3StorageManager
        
        # Load and validate configuration
        config = validate_config()
        s3_config = config.get("s3_config", {})
        
        # Initialize S3 storage manager
        s3_storage = S3StorageManager(s3_config)
        
        if s3_storage.is_available():
            print("✅ S3StorageManager initialized successfully!")
            
            # Test connection
            if s3_storage._test_connection():
                print("✅ S3StorageManager connection test passed!")
                return True
            else:
                print("❌ S3StorageManager connection test failed!")
                return False
        else:
            print("❌ S3StorageManager not available")
            return False
            
    except Exception as e:
        print(f"❌ S3StorageManager test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 AWS S3 Credentials Test")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_boto3_import,
        test_s3_connection,
        test_s3_storage_manager
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All tests passed! Your AWS S3 setup is working correctly.")
        print("✅ You can now use S3 storage in the Creative Automation Pipeline.")
    else:
        print(f"⚠️  {passed}/{total} tests passed.")
        print("💡 Please check the failed tests and fix the issues.")
        print("📖 See AWS_SETUP_GUIDE.md for detailed setup instructions.")

if __name__ == "__main__":
    main()
