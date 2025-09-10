#!/usr/bin/env python3
"""
Test script for Google Veo 3 video generation.
This script will help you test video generation with Google Veo 3.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src")))

from src.pipeline.models import CampaignBrief, Product, ContentType, VideoFormat
from src.pipeline.google_veo3_generator import GoogleVeo3Generator

async def test_veo3_generation():
    """Test Google Veo 3 video generation."""
    
    # Check if API key is set
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ Google Veo 3 API key not found!")
        print("\n📋 To set up Google Veo 3:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Create an API key")
        print("3. Set it as an environment variable:")
        print("   PowerShell: $env:GOOGLE_AI_API_KEY='your_api_key_here'")
        print("   CMD: set GOOGLE_AI_API_KEY=your_api_key_here")
        print("\n🔑 Or enter your API key now:")
        api_key = input("Enter your Google AI API key: ").strip()
        if api_key:
            os.environ['GOOGLE_AI_API_KEY'] = api_key
        else:
            print("❌ No API key provided. Exiting.")
            return
    
    print("✅ Google Veo 3 API key found!")
    
    # Create test product
    product = Product(
        name="Nike Air Max 270",
        description="Comfortable running shoes with Air Max technology for all-day comfort",
        category="Sports",
        price=150.0,
        features=["Air Max cushioning", "Breathable mesh", "Durable outsole"],
        target_demographic="Athletes and fitness enthusiasts"
    )
    
    # Create test campaign brief
    campaign_brief = CampaignBrief(
        campaign_id="test_veo3",
        campaign_name="Nike Air Max Test",
        products=[product],
        target_region="North America",
        target_audience="Athletes and fitness enthusiasts",
        campaign_message="Experience ultimate comfort with Nike Air Max 270",
        aspect_ratios=["9:16"],  # Vertical for mobile
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
    veo3_config = {
        "api_key": api_key,
        "quality": "High"
    }
    
    print("🎬 Initializing Google Veo 3 generator...")
    generator = GoogleVeo3Generator(veo3_config)
    
    print("🚀 Starting video generation...")
    print(f"📱 Product: {product.name}")
    print(f"💬 Message: {campaign_brief.campaign_message}")
    print(f"⏱️  Duration: {campaign_brief.video_duration} seconds")
    print(f"📐 Format: {campaign_brief.video_format.value}")
    
    try:
        # Generate video
        video_path = await generator.generate_video_ad(product, campaign_brief)
        
        if video_path and Path(video_path).exists():
            print(f"✅ Video generated successfully!")
            print(f"📁 Location: {video_path}")
            print(f"📊 File size: {Path(video_path).stat().st_size / (1024*1024):.2f} MB")
        else:
            print("❌ Video generation failed - no output file created")
            
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        print("💡 This might be due to:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API rate limits")
        print("   - Google Veo 3 service issues")

if __name__ == "__main__":
    print("🎬 Google Veo 3 Video Generation Test")
    print("=" * 50)
    asyncio.run(test_veo3_generation())

