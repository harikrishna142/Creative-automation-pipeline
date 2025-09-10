"""
AWS S3 Storage Module for Creative Automation Pipeline

This module handles all S3 operations including:
- Campaign JSON storage
- Asset uploads and downloads
- Generated creative storage
- File organization and retrieval
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from .models import CampaignBrief, CampaignOutput, GeneratedCreative, GeneratedVideo


class S3StorageManager:
    """Manages all S3 storage operations for the creative automation pipeline."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize S3 storage manager.
        
        Args:
            config: Configuration dictionary containing S3 settings
        """
        self.bucket_name = config.get("s3_bucket_name", "creative-automation-pipeline")
        self.region = config.get("s3_region", "us-east-1")
        self.prefix = config.get("s3_prefix", "campaigns")
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=config.get("aws_access_key_id"),
                aws_secret_access_key=config.get("aws_secret_access_key")
            )
            
            # Test connection
            self._test_connection()
            logger.info(f"S3 storage initialized successfully. Bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.warning("AWS credentials not found. S3 storage will be disabled.")
            self.s3_client = None
        except Exception as e:
            logger.error(f"Failed to initialize S3 storage: {e}")
            self.s3_client = None
    
    def _test_connection(self) -> bool:
        """Test S3 connection and bucket access."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3 bucket '{self.bucket_name}' not found")
            elif error_code == '403':
                logger.error(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                logger.error(f"S3 connection error: {e}")
            return False
    
    def _get_s3_key(self, file_type: str, campaign_id: str, filename: str = None) -> str:
        """
        Generate S3 key for file organization.
        
        Args:
            file_type: Type of file (campaigns, assets, creatives, videos)
            campaign_id: Campaign identifier
            filename: Optional filename
            
        Returns:
            S3 key path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if file_type == "campaigns":
            return f"{self.prefix}/campaigns/{campaign_id}/campaign_brief.json"
        elif file_type == "assets":
            return f"{self.prefix}/assets/{campaign_id}/{filename}"
        elif file_type == "creatives":
            return f"{self.prefix}/creatives/{campaign_id}/{filename}"
        elif file_type == "videos":
            return f"{self.prefix}/videos/{campaign_id}/{filename}"
        else:
            return f"{self.prefix}/{file_type}/{campaign_id}/{filename}"
    
    def _get_s3_url(self, s3_key: str) -> str:
        """Generate S3 URL for a given key."""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    async def store_campaign_brief(self, campaign_brief: CampaignBrief, campaign_id: str) -> Optional[str]:
        """
        Store campaign brief JSON to S3.
        
        Args:
            campaign_brief: Campaign brief object
            campaign_id: Campaign identifier
            
        Returns:
            S3 URL of stored campaign brief or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Campaign brief not stored.")
            return None
        
        try:
            # Convert to JSON
            campaign_data = campaign_brief.model_dump()
            campaign_json = json.dumps(campaign_data, indent=2, default=str)
            
            # Generate S3 key
            s3_key = self._get_s3_key("campaigns", campaign_id)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=campaign_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_brief.campaign_name,
                    'created_at': datetime.now().isoformat(),
                    'file_type': 'campaign_brief'
                }
            )
            
            s3_url = self._get_s3_url(s3_key)
            logger.info(f"Campaign brief stored in S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to store campaign brief in S3: {e}")
            return None
    
    async def store_campaign_output(self, campaign_output: CampaignOutput, campaign_id: str) -> Optional[str]:
        """
        Store campaign output JSON to S3.
        
        Args:
            campaign_output: Campaign output object
            campaign_id: Campaign identifier
            
        Returns:
            S3 URL of stored campaign output or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Campaign output not stored.")
            return None
        
        try:
            # Convert to JSON
            output_data = campaign_output.model_dump()
            output_json = json.dumps(output_data, indent=2, default=str)
            
            # Generate S3 key
            s3_key = self._get_s3_key("campaigns", campaign_id, "campaign_output.json")
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=output_json.encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'campaign_id': campaign_id,
                    'campaign_name': campaign_output.campaign_name,
                    'created_at': datetime.now().isoformat(),
                    'file_type': 'campaign_output',
                    'total_creatives': str(len(campaign_output.generated_creatives)),
                    'total_videos': str(len(campaign_output.generated_videos) if campaign_output.generated_videos else 0)
                }
            )
            
            s3_url = self._get_s3_url(s3_key)
            logger.info(f"Campaign output stored in S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to store campaign output in S3: {e}")
            return None
    
    async def upload_asset(self, local_file_path: Union[str, Path], campaign_id: str, 
                          asset_category: str = "general") -> Optional[str]:
        """
        Upload an asset file to S3.
        
        Args:
            local_file_path: Path to local file
            campaign_id: Campaign identifier
            asset_category: Category of asset (brand_logo, avatar, background, etc.)
            
        Returns:
            S3 URL of uploaded asset or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Asset not uploaded.")
            return None
        
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_file_path}")
                return None
            
            # Generate S3 key
            filename = f"{asset_category}/{local_path.name}"
            s3_key = self._get_s3_key("assets", campaign_id, filename)
            
            # Upload to S3
            with open(local_path, 'rb') as file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file,
                    ContentType=self._get_content_type(local_path.suffix),
                    Metadata={
                        'campaign_id': campaign_id,
                        'asset_category': asset_category,
                        'original_filename': local_path.name,
                        'file_size': str(local_path.stat().st_size),
                        'uploaded_at': datetime.now().isoformat()
                    }
                )
            
            s3_url = self._get_s3_url(s3_key)
            logger.info(f"Asset uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload asset to S3: {e}")
            return None
    
    async def upload_creative(self, local_file_path: Union[str, Path], campaign_id: str,
                             product_name: str, aspect_ratio: str, variation_num: int) -> Optional[str]:
        """
        Upload a generated creative to S3.
        
        Args:
            local_file_path: Path to local creative file
            campaign_id: Campaign identifier
            product_name: Name of the product
            aspect_ratio: Aspect ratio of the creative
            variation_num: Variation number
            
        Returns:
            S3 URL of uploaded creative or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Creative not uploaded.")
            return None
        
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"Local creative file not found: {local_file_path}")
                return None
            
            # Generate S3 key with organized structure
            filename = f"{product_name}/{aspect_ratio}/{local_path.name}"
            s3_key = self._get_s3_key("creatives", campaign_id, filename)
            
            # Upload to S3
            with open(local_path, 'rb') as file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file,
                    ContentType=self._get_content_type(local_path.suffix),
                    Metadata={
                        'campaign_id': campaign_id,
                        'product_name': product_name,
                        'aspect_ratio': aspect_ratio,
                        'variation_num': str(variation_num),
                        'file_type': 'creative',
                        'uploaded_at': datetime.now().isoformat()
                    }
                )
            
            s3_url = self._get_s3_url(s3_key)
            logger.info(f"Creative uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload creative to S3: {e}")
            return None
    
    async def upload_video(self, local_file_path: Union[str, Path], campaign_id: str,
                          product_name: str, video_format: str) -> Optional[str]:
        """
        Upload a generated video to S3.
        
        Args:
            local_file_path: Path to local video file
            campaign_id: Campaign identifier
            product_name: Name of the product
            video_format: Video format (youtube_shorts, instagram_reels, etc.)
            
        Returns:
            S3 URL of uploaded video or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Video not uploaded.")
            return None
        
        try:
            local_path = Path(local_file_path)
            if not local_path.exists():
                logger.error(f"Local video file not found: {local_file_path}")
                return None
            
            # Generate S3 key
            filename = f"{product_name}/{video_format}/{local_path.name}"
            s3_key = self._get_s3_key("videos", campaign_id, filename)
            
            # Upload to S3
            with open(local_path, 'rb') as file:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file,
                    ContentType=self._get_content_type(local_path.suffix),
                    Metadata={
                        'campaign_id': campaign_id,
                        'product_name': product_name,
                        'video_format': video_format,
                        'file_type': 'video',
                        'uploaded_at': datetime.now().isoformat()
                    }
                )
            
            s3_url = self._get_s3_url(s3_key)
            logger.info(f"Video uploaded to S3: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload video to S3: {e}")
            return None
    
    async def download_file(self, s3_url: str, local_path: Union[str, Path]) -> bool:
        """
        Download a file from S3 to local storage.
        
        Args:
            s3_url: S3 URL of the file
            local_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            logger.warning("S3 client not available. File not downloaded.")
            return False
        
        try:
            # Parse S3 URL to get bucket and key
            parsed_url = urlparse(s3_url)
            bucket_name = parsed_url.netloc.split('.')[0]
            s3_key = parsed_url.path.lstrip('/')
            
            # Download file
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(bucket_name, s3_key, str(local_path))
            logger.info(f"File downloaded from S3: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download file from S3: {e}")
            return False
    
    async def list_campaign_files(self, campaign_id: str) -> Dict[str, List[str]]:
        """
        List all files for a specific campaign.
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            Dictionary with file lists by type
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Cannot list files.")
            return {}
        
        try:
            files = {
                'campaigns': [],
                'assets': [],
                'creatives': [],
                'videos': []
            }
            
            # List objects with campaign prefix
            prefix = f"{self.prefix}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if campaign_id in key:
                        if '/campaigns/' in key:
                            files['campaigns'].append(self._get_s3_url(key))
                        elif '/assets/' in key:
                            files['assets'].append(self._get_s3_url(key))
                        elif '/creatives/' in key:
                            files['creatives'].append(self._get_s3_url(key))
                        elif '/videos/' in key:
                            files['videos'].append(self._get_s3_url(key))
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list campaign files: {e}")
            return {}
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension."""
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    async def get_presigned_url(self, s3_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to S3 object.
        
        Args:
            s3_url: S3 URL of the object
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.s3_client:
            logger.warning("S3 client not available. Cannot generate presigned URL.")
            return None
        
        try:
            # Parse S3 URL to get bucket and key
            parsed_url = urlparse(s3_url)
            bucket_name = parsed_url.netloc.split('.')[0]
            s3_key = parsed_url.path.lstrip('/')
            
            # Generate presigned URL
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            return presigned_url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if S3 storage is available."""
        return self.s3_client is not None
