#!/usr/bin/env python3
"""
Test script to verify Google Veo 3 integration in the creative pipeline.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src")))

def test_veo3_setup():
    """Test if Google Veo 3 is properly set up."""
    print("🔍 Testing Google Veo 3 Setup")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print("✅ Google AI API key found")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ Google AI API key not found")
        print("   Please set GOOGLE_AI_API_KEY environment variable")
        return False
    
    # Check if google-genai is installed
    try:
        import google.genai as genai
        print("✅ google-genai package is installed")
    except ImportError:
        print("❌ google-genai package not found")
        print("   Please install: pip install google-genai")
        return False
    
    # Test Google Veo 3 generator initialization
    try:
        from pipeline.google_veo3_generator import GoogleVeo3Generator
        
        config = {
            "api_key": api_key,
            "quality": "High"
        }
        
        generator = GoogleVeo3Generator(config)
        print("✅ Google Veo 3 generator initialized successfully")
        
        if generator.client:
            print("✅ Google AI client is ready")
        else:
            print("⚠️  Google AI client not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize Google Veo 3 generator: {e}")
        return False
    
    return True

async def test_veo3_generation():
    """Test Google Veo 3 video generation."""
    print("\n🎬 Testing Google Veo 3 Video Generation")
    print("=" * 50)
    
    try:
        from pipeline.models import CampaignBrief, Product, ContentType, VideoFormat
        from pipeline.google_veo3_generator import GoogleVeo3Generator
        
        # Create test product
        product = Product(
            name="Nike Air Max 270",
            description="Comfortable running shoes with Air Max technology for all-day comfort and performance",
            category="Sports",
            price=150.0,
            features=["Air Max cushioning", "Breathable mesh", "Durable outsole"],
            target_demographic="Athletes and fitness enthusiasts"
        )
        
        # Create test campaign brief
        campaign_brief = CampaignBrief(
            campaign_id="test_veo3_pipeline",
            campaign_name="Nike Air Max Test Campaign",
            products=[product],
            target_region="North America",
            target_audience="Athletes and fitness enthusiasts",
            campaign_message="Experience ultimate comfort with Nike Air Max 270",
            aspect_ratios=["9:16"],
            language="en",
            brand_guidelines={
                "primary_color": "#FF6B35",
                "secondary_color": "#FFFFFF",
                "accent_color": "#000000"
            },
            content_type=ContentType.VIDEO,
            video_format=VideoFormat.YOUTUBE_SHORTS,
            video_duration=8,
            include_music=True,
            include_voice_over=True
        )
        
        # Initialize Google Veo 3 generator
        config = {
            "api_key": os.getenv('GOOGLE_AI_API_KEY'),
            "quality": "High"
        }
        
        generator = GoogleVeo3Generator(config)
        
        print(f"📱 Product: {product.name}")
        print(f"💬 Message: {campaign_brief.campaign_message}")
        print(f"⏱️  Duration: {campaign_brief.video_duration} seconds")
        print(f"📐 Format: {campaign_brief.video_format.value}")
        
        print("\n🚀 Starting video generation...")
        video_path = await generator.generate_video_ad(product, campaign_brief)
        
        if video_path and Path(video_path).exists():
            print(f"✅ Video generated successfully!")
            print(f"📁 Location: {video_path}")
            print(f"📊 File size: {Path(video_path).stat().st_size / (1024*1024):.2f} MB")
            return True
        else:
            print("❌ Video generation failed - no output file created")
            return False
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        return False

async def main():
    """Main test function."""
    print("🎬 Google Veo 3 Pipeline Integration Test")
    print("=" * 60)
    
    # Test setup
    if not test_veo3_setup():
        print("\n❌ Setup test failed. Please fix the issues above.")
        return
    
    # Test generation
    success = await test_veo3_generation()
    
    if success:
        print("\n🎉 All tests passed! Google Veo 3 is ready to use.")
    else:
        print("\n❌ Video generation test failed.")
        print("💡 This might be due to:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API rate limits")
        print("   - Google Veo 3 service issues")

if __name__ == "__main__":
    asyncio.run(main())

