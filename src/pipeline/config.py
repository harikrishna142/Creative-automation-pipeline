"""
Configuration management for the Creative Automation Pipeline.

This module handles loading configuration from environment variables and provides
default configurations for different components.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_file = Path(".env")
if env_file.exists():
    try:
        load_dotenv(env_file)
    except (UnicodeDecodeError, Exception) as e:
        print(f"Warning: Could not load .env file: {e}")
        print("Continuing without .env file...")


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and return a structured config dictionary.
    
    Returns:
        Configuration dictionary with all settings
    """
    config = {
        # AI Configuration
        "ai_config": {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "google_api_key": os.getenv("GOOGLE_API_KEY"),
            "dalle_model": os.getenv("DALLE_MODEL", "dall-e-3"),
            "gpt_model": os.getenv("GPT_MODEL", "gpt-4.1"),
            "fallback_mode": os.getenv("FALLBACK_MODE", "true").lower() == "true"
        },
        
        # S3 Configuration
        "s3_config": {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "s3_bucket_name": os.getenv("S3_BUCKET_NAME", "creative-automation-pipeline"),
            "s3_region": os.getenv("S3_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1")),
            "s3_prefix": os.getenv("S3_PREFIX", "campaigns")
        },
        
        # Template Configuration
        "template_config": {
            "default_font_size": int(os.getenv("DEFAULT_FONT_SIZE", "48")),
            "text_color": os.getenv("TEXT_COLOR", "#FFFFFF"),
            "outline_color": os.getenv("OUTLINE_COLOR", "#000000"),
            "brand_templates_enabled": os.getenv("BRAND_TEMPLATES_ENABLED", "true").lower() == "true"
        },
        
        # Video Configuration
        "video_config": {
            "use_veo3": os.getenv("USE_VEO3", "false").lower() == "true",
            "video_quality": os.getenv("VIDEO_QUALITY", "standard"),
            "video_duration": int(os.getenv("VIDEO_DURATION", "8")),
            "include_music": os.getenv("INCLUDE_MUSIC", "true").lower() == "true",
            "include_voice_over": os.getenv("INCLUDE_VOICE_OVER", "true").lower() == "true"
        },
        
        # Quality Configuration
        "quality_config": {
            "min_quality_score": float(os.getenv("MIN_QUALITY_SCORE", "0.7")),
            "enable_quality_checks": os.getenv("ENABLE_QUALITY_CHECKS", "true").lower() == "true",
            "auto_retry_failed": os.getenv("AUTO_RETRY_FAILED", "true").lower() == "true"
        },
        
        # Application Configuration
        "app_config": {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "output_dir": os.getenv("OUTPUT_DIR", "output"),
            "max_concurrent_generations": int(os.getenv("MAX_CONCURRENT_GENERATIONS", "3")),
            "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "60"))
        }
    }
    
    return config


def get_s3_config() -> Dict[str, Any]:
    """
    Get S3-specific configuration.
    
    Returns:
        S3 configuration dictionary
    """
    return load_config()["s3_config"]


def get_ai_config() -> Dict[str, Any]:
    """
    Get AI-specific configuration.
    
    Returns:
        AI configuration dictionary
    """
    return load_config()["ai_config"]


def validate_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate configuration and return validated config with warnings for missing keys.
    
    Args:
        config: Optional configuration dictionary to validate
        
    Returns:
        Validated configuration dictionary
    """
    if config is None:
        config = load_config()
    
    warnings = []
    
    # Check for required API keys
    if not config["ai_config"]["openai_api_key"]:
        warnings.append("OPENAI_API_KEY not set - AI image generation will be disabled")
    
    if not config["s3_config"]["aws_access_key_id"] or not config["s3_config"]["aws_secret_access_key"]:
        warnings.append("AWS credentials not set - S3 storage will be disabled")
    
    if not config["s3_config"]["s3_bucket_name"]:
        warnings.append("S3_BUCKET_NAME not set - using default bucket name")
    
    # Print warnings
    for warning in warnings:
        print(f"⚠️  Configuration Warning: {warning}")
    
    return config


def create_default_config_file(output_path: str = "config.json") -> None:
    """
    Create a default configuration file with all available options.
    
    Args:
        output_path: Path where to save the configuration file
    """
    import json
    
    default_config = {
        "ai_config": {
            "openai_api_key": "your_openai_api_key_here",
            "google_api_key": "your_google_api_key_here",
            "dalle_model": "dall-e-3",
            "gpt_model": "gpt-4.1",
            "fallback_mode": True
        },
        "s3_config": {
            "aws_access_key_id": "your_aws_access_key_id_here",
            "aws_secret_access_key": "your_aws_secret_access_key_here",
            "s3_bucket_name": "creative-automation-pipeline",
            "s3_region": "us-east-1",
            "s3_prefix": "campaigns"
        },
        "template_config": {
            "default_font_size": 48,
            "text_color": "#FFFFFF",
            "outline_color": "#000000",
            "brand_templates_enabled": True
        },
        "video_config": {
            "use_veo3": False,
            "video_quality": "standard",
            "video_duration": 8,
            "include_music": True,
            "include_voice_over": True
        },
        "quality_config": {
            "min_quality_score": 0.7,
            "enable_quality_checks": True,
            "auto_retry_failed": True
        },
        "app_config": {
            "debug": False,
            "log_level": "INFO",
            "output_dir": "output",
            "max_concurrent_generations": 3,
            "request_timeout": 60
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"Default configuration file created: {output_path}")


if __name__ == "__main__":
    # Test configuration loading
    config = validate_config()
    print("✅ Configuration loaded successfully")
    print(f"S3 Bucket: {config['s3_config']['s3_bucket_name']}")
    print(f"OpenAI API Key: {'Set' if config['ai_config']['openai_api_key'] else 'Not Set'}")
    print(f"AWS Credentials: {'Set' if config['s3_config']['aws_access_key_id'] else 'Not Set'}")
