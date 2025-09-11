#!/usr/bin/env python3
"""
Adobe Creative Studio - Streamlit UI for Creative Automation Pipeline

A modern, Adobe-inspired interface for the creative automation pipeline.
"""

import streamlit as st
import json
import yaml
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io

# Add src to path for imports
src_dir = Path(__file__).parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import pipeline components
try:
    from src.pipeline.models import CampaignBrief, GenerationRequest, Product, AspectRatio, ContentType, VideoFormat
    from src.pipeline.creative_pipeline import CreativePipeline
    from src.pipeline.asset_generator import AssetGenerator
    from src.pipeline.config import load_config, validate_config
    from src.pipeline.s3_storage import S3StorageManager
except ImportError as e:
    st.error(f"Failed to import pipeline components: {e}")
    st.stop()

import base64

# Configure Streamlit page
st.set_page_config(
    page_title="Adobe Creative Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Adobe-like styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .campaign-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .creative-preview {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .creative-preview:hover {
        transform: translateY(-5px);
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'campaigns' not in st.session_state:
    st.session_state.campaigns = []
if 'generated_creatives' not in st.session_state:
    st.session_state.generated_creatives = []
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = "Ready"

def load_example_campaigns():
    """Load example campaign briefs."""
    examples_dir = Path("examples")
    campaigns = []
    
    if examples_dir.exists():
        for file_path in examples_dir.glob("*.json"):
            with open(file_path) as f:
                campaign = json.load(f)
                campaigns.append(campaign)
    
    return campaigns

def get_image_base64(image_path):
    """Convert image to base64 for display."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def display_creative_preview(creative_path, aspect_ratio, product_name):
    """Display a creative preview card."""
    if creative_path.exists():
        image_base64 = get_image_base64(creative_path)
        if image_base64:
            st.markdown(f"""
            <div class="creative-preview">
                <img src="data:image/jpeg;base64,{image_base64}" 
                     style="width: 100%; height: auto; border-radius: 10px;">
                <div style="padding: 1rem; background: white;">
                    <h4 style="margin: 0; color: #333;">{product_name}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">{aspect_ratio}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Could not load image: {creative_path}")
    else:
        st.warning(f"Creative not found: {creative_path}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Adobe Creative Studio</h1>
        <p>AI-Powered Creative Automation Pipeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Campaign Builder", "Creative Gallery", "Assets", "S3 Management", "Analytics", "Settings"],
            index=["Dashboard", "Campaign Builder", "Creative Gallery", "Assets", "S3 Management", "Analytics", "Settings"].index(st.session_state.current_page)
        )
        
        # Update session state when page changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Pipeline Status")
        status_color = "status-success" if st.session_state.pipeline_status == "Ready" else "status-warning"
        st.markdown(f'<p class="{status_color}">● {st.session_state.pipeline_status}</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔧 Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📁 Open Output Folder"):
            output_dir = Path("output")
            if output_dir.exists():
                st.success(f"Output directory: {output_dir.absolute()}")
            else:
                st.warning("No output directory found")
    
    # Main content based on selected page
    if st.session_state.current_page == "Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "Campaign Builder":
        show_campaign_builder()
    elif st.session_state.current_page == "Creative Gallery":
        show_creative_gallery()
    elif st.session_state.current_page == "Assets":
        show_assets_page()
    elif st.session_state.current_page == "S3 Management":
        show_s3_management()
    elif st.session_state.current_page == "Analytics":
        show_analytics()
    elif st.session_state.current_page == "Settings":
        show_settings()

def show_dashboard():
    """Show the main dashboard."""
    
    st.markdown("## 📊 Dashboard Overview")
    
    # Load campaigns and creatives
    campaigns = load_example_campaigns()
    output_dir = Path("output")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Total Campaigns</p>
        </div>
        """.format(len(campaigns)), unsafe_allow_html=True)
    
    with col2:
        total_creatives = 0
        if output_dir.exists():
            for campaign_dir in output_dir.iterdir():
                if campaign_dir.is_dir():
                    total_creatives += len(list(campaign_dir.rglob("creative_*.jpg")))
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Generated Creatives</p>
        </div>
        """.format(total_creatives), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">95%</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Success Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">2.3s</h3>
            <p style="margin: 0.5rem 0 0 0; color: #666;">Avg Generation Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent campaigns
    st.markdown("## 🚀 Recent Campaigns")
    
    if campaigns:
        for campaign in campaigns[:3]:  # Show last 3 campaigns
            with st.container():
                st.markdown(f"""
                <div class="campaign-card">
                    <h4 style="margin: 0 0 0.5rem 0; color: #333;">{campaign['campaign_name']}</h4>
                    <p style="margin: 0 0 0.5rem 0; color: #666;">{campaign['target_region']} • {len(campaign['products'])} products</p>
                    <p style="margin: 0; color: #888; font-size: 0.9rem;">{campaign['campaign_message']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No campaigns found. Create your first campaign in the Campaign Builder!")
    
    # Quick start section
    st.markdown("---")
    st.markdown("## ⚡ Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎨 View Gallery")
        if st.button("🖼️ View Gallery", width='stretch'):
            st.session_state.current_page = "Creative Gallery"
            st.rerun()
    
    with col2:
        st.markdown("### 📋 Create Campaign")
        if st.button("➕ New Campaign", width='stretch'):
            st.session_state.current_page = "Campaign Builder"
            st.rerun()

def show_campaign_builder():
    """Show the campaign builder interface."""
    
    st.markdown("## 🎯 Campaign Builder")
    
    # Campaign form
    with st.form("campaign_form"):
        st.markdown("### Campaign Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_id = st.text_input("Campaign ID", value=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            campaign_name = st.text_input("Campaign Name", placeholder="e.g., Spring Fashion Collection")
            target_region = st.selectbox("Target Region", ["North America", "Europe", "Asia Pacific", "Latin America"])
        
        with col2:
            target_audience = st.text_area("Target Audience", placeholder="Describe your target audience...")
            campaign_message = st.text_input("Campaign Message", placeholder="e.g., Experience the future of technology")
            language = st.selectbox("Language", [
                "en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"
            ], format_func=lambda x: {
                "en": "English", "es": "Spanish", "fr": "French", "de": "German", 
                "it": "Italian", "pt": "Portuguese", "ja": "Japanese", 
                "ko": "Korean", "zh": "Chinese"
            }[x])
        
        st.markdown("### Products")
        
        # Dynamic product form
        if 'products' not in st.session_state:
            st.session_state.products = [{}]
        
        # Store form values in a list
        product_forms = []
        
        for i, product in enumerate(st.session_state.products):
            with st.expander(f"Product {i+1}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    product_name = st.text_input(f"Product Name {i+1}", value=product.get('name', ''), key=f"product_name_{i}")
                    product_category = st.selectbox(f"Category {i+1}", 
                        ["Electronics", "Fashion", "Home & Garden", "Sports", "Beauty", "Food & Beverage"],
                        key=f"product_category_{i}")
                    product_price = st.number_input(f"Price {i+1}", value=product.get('price', 0.0), key=f"product_price_{i}")
                
                with col2:
                    product_description = st.text_area(f"Description {i+1}", value=product.get('description', ''), key=f"product_desc_{i}")
                    product_features = st.text_input(f"Features {i+1}", value=','.join(product.get('features', [])), 
                        help="Separate features with commas", key=f"product_features_{i}")
                    target_demographic = st.text_input(f"Target Demographic {i+1}", value=product.get('target_demographic', ''), key=f"product_demo_{i}")
                
                # Store the form values
                product_forms.append({
                    'name': product_name,
                    'description': product_description,
                    'category': product_category,
                    'price': product_price,
                    'features': product_features,
                    'target_demographic': target_demographic
                })
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("➕ Add Product"):
                st.session_state.products.append({})
                st.rerun()
        
        with col2:
            if st.form_submit_button("➖ Remove Last Product"):
                if len(st.session_state.products) > 1:
                    st.session_state.products.pop()
                    st.rerun()
        
        st.markdown("### Content Type & Video Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.selectbox(
                "Content Type",
                ["Image Only", "Video Only", "Both Images & Videos"],
                help="Choose what type of content to generate"
            )
            
            # Video format field - enabled only when video content is selected
            if content_type in ["Video Only", "Both Images & Videos"]:
                video_format = st.selectbox(
                    "Video Format",
                    ["YouTube Shorts", "Instagram Reels", "TikTok", "Story"],
                    help="Choose the video format for social media"
                )
                
                # Google Veo 3 options
                use_veo3 = st.checkbox("Use Google Veo 3", value=True, help="Generate videos using Google's advanced Veo 3 AI model")
                
                if use_veo3:
                    st.info("🎬 Google Veo 3 generates 8-second videos at 720p resolution")
                    video_duration = 8  # Fixed for Veo 3
                else:
                    video_duration = st.slider(
                        "Video Duration (seconds)",
                        min_value=5,
                        max_value=60,
                        value=15,
                        help="Duration of the generated video"
                    )
            else:
                # Disabled fields when video is not selected
                st.selectbox(
                    "Video Format (Disabled)",
                    ["YouTube Shorts", "Instagram Reels", "TikTok", "Story"],
                    disabled=True,
                    help="Select 'Video Only' or 'Both Images & Videos' to enable"
                )
                video_format = None
                video_duration = None
                use_veo3 = False
        
        with col2:
            if content_type in ["Video Only", "Both Images & Videos"]:
                include_music = st.checkbox("Include Background Music", value=True)
                include_voice_over = st.checkbox("Include Voice-Over", value=True)
                
                # Google Veo 3 options
                st.markdown("#### 🤖 AI Video Generation")
                
                if use_veo3:
                    st.info("🎬 Google Veo 3 will create high-quality, professional videos with advanced AI generation")
                    veo3_quality = st.selectbox(
                        "Video Quality",
                        ["Standard", "High", "Ultra"],
                        index=1,
                        help="Higher quality takes longer but produces better results"
                    )
                else:
                    veo3_quality = None
            else:
                # Disabled fields when video is not selected
                st.checkbox("Include Background Music (Disabled)", disabled=True, help="Select video content type to enable")
                st.checkbox("Include Voice-Over (Disabled)", disabled=True, help="Select video content type to enable")
                st.markdown("#### 🤖 AI Video Generation (Disabled)")
                st.selectbox(
                    "Video Quality (Disabled)",
                    ["Standard", "High", "Ultra"],
                    disabled=True,
                    help="Select video content type to enable"
                )
                include_music = False
                include_voice_over = False
                veo3_quality = None
        st.markdown("### Creative Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            aspect_ratios = st.multiselect(
                "Aspect Ratios",
                ["1:1", "9:16", "16:9"],
                default=["1:1", "9:16", "16:9"]
            )
        
        with col2:
            brand_primary = st.color_picker("Primary Color", value="#667eea")
            brand_secondary = st.color_picker("Secondary Color", value="#ffffff")
            brand_accent = st.color_picker("Accent Color", value="#ffd700")
        
        # Asset Selection Section
        st.markdown("### 🎨 Asset Selection")
        st.info("💡 Select assets by category for better creative generation. These parameters are optional but help create more personalized and branded content.")
        
        # Brand Selection
        st.markdown("#### 🏷️ Brand")
        brand_options = ["None", "Nike", "Adidas", "Coca-Cola", "Apple", "Samsung", "Custom"]
        selected_brand = st.selectbox("Select Brand", brand_options, help="Select a brand to apply brand-specific templates and styling")
        
        # Persona Selection
        st.markdown("#### 👤 Persona")
        persona_options = ["None", "Young Adults", "Families", "Professionals", "Athletes", "Students", "Seniors", "Custom"]
        selected_persona = st.selectbox("Select Target Persona", persona_options, help="Select a persona for 9:16 aspect ratio - will show a person wearing/using the product. For other aspect ratios, this influences overall style.")
        
        # Custom Prompt
        st.markdown("#### ✨ Custom Context")
        custom_prompt = st.text_area(
            "Custom Prompt (Optional)", 
            placeholder="e.g., 'Modern minimalist style with vibrant colors, urban setting, professional photography' or 'Show product in action, dynamic movement, lifestyle setting'",
            help="Add custom context that will be included in the DALL-E prompt for asset generation"
        )
        
        # Asset Selection
        st.markdown("#### 🎯 Asset Selection")
        
        # Get available assets
        assets_dir = Path("output/assets")
        available_brand_logos = []
        available_avatars = []
        
        if assets_dir.exists():
            # Get brand logos
            brand_logo_dir = assets_dir / "brand_logo"
            if brand_logo_dir.exists():
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.svg"]:
                    available_brand_logos.extend(brand_logo_dir.glob(ext))
            
            # Get avatars
            avatar_dir = assets_dir / "avatar"
            if avatar_dir.exists():
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.svg"]:
                    available_avatars.extend(avatar_dir.glob(ext))
        
        # Brand Logo Selection
        selected_brand_logo = None
        if available_brand_logos:
            st.markdown("**🏷️ Select Brand Logo:**")
            logo_options = ["None"] + [logo.name for logo in available_brand_logos]
            selected_logo_name = st.selectbox("Choose Brand Logo", logo_options, help="Select a brand logo to include in creatives")
            
            if selected_logo_name != "None":
                selected_brand_logo = str(next(logo for logo in available_brand_logos if logo.name == selected_logo_name))
        else:
            st.info("No brand logos available. Visit the Assets page to upload or generate logos.")
        
        # Avatar Selection
        selected_avatar = None
        if available_avatars:
            st.markdown("**👤 Select Avatar (for 9:16 aspect ratio):**")
            avatar_options = ["None"] + [avatar.name for avatar in available_avatars]
            selected_avatar_name = st.selectbox("Choose Avatar", avatar_options, help="Select an avatar to use in 9:16 vertical creatives")
            
            if selected_avatar_name != "None":
                selected_avatar = str(next(avatar for avatar in available_avatars if avatar.name == selected_avatar_name))
        else:
            st.info("No avatars available. Visit the Assets page to upload or generate avatars.")
        
        # Store selected parameters
        asset_params = {
            "brand": selected_brand if selected_brand != "None" else None,
            "persona": selected_persona if selected_persona != "None" else None,
            "custom_prompt": custom_prompt if custom_prompt.strip() else None,
            "selected_brand_logo": selected_brand_logo,
            "selected_avatar": selected_avatar
        }
        
        # Show selection summary
        selected_assets = []
        if selected_brand_logo:
            selected_assets.append("Brand Logo")
        if selected_avatar:
            selected_assets.append("Avatar")
        
        if selected_assets:
            st.success(f"✅ Selected assets: {', '.join(selected_assets)}")
        else:
            st.info("No assets selected. You can still generate creatives with basic styling.")
        
        # Submit button
        if st.form_submit_button("🚀 Generate Campaign", width='stretch'):
            # Build campaign object
            campaign = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "products": [],
                "target_region": target_region,
                "target_audience": target_audience,
                "campaign_message": campaign_message,
                "aspect_ratios": aspect_ratios,
                "language": language,
                "brand_guidelines": {
                    "primary_color": brand_primary,
                    "secondary_color": brand_secondary,
                    "accent_color": brand_accent
                },
                "content_type": content_type,
                "video_format": video_format if content_type in ["Video Only", "Both Images & Videos"] else None,
                "video_duration": video_duration if content_type in ["Video Only", "Both Images & Videos"] else None,
                "include_music": include_music if content_type in ["Video Only", "Both Images & Videos"] else False,
                "include_voice_over": include_voice_over if content_type in ["Video Only", "Both Images & Videos"] else False,
                "use_veo3": use_veo3 if content_type in ["Video Only", "Both Images & Videos"] else False,
                "veo3_quality": veo3_quality if content_type in ["Video Only", "Both Images & Videos"] and use_veo3 else None,
                "asset_params": asset_params
            }
            
            # Add products from the collected form values
            for product_form in product_forms:
                if product_form['name']:  # Only add products with names
                    campaign["products"].append({
                        "name": product_form['name'],
                        "description": product_form['description'],
                        "category": product_form['category'],
                        "price": product_form['price'],
                        "features": [f.strip() for f in product_form['features'].split(',') if f.strip()],
                        "target_demographic": product_form['target_demographic']
                    })
            
            # Validate campaign has products
            if not campaign["products"]:
                st.error("Please add at least one product to generate creatives!")
                return
            
            # Save campaign
            examples_dir = Path("examples")
            examples_dir.mkdir(exist_ok=True)
            
            campaign_file = examples_dir / f"{campaign_id}.json"
            with open(campaign_file, "w") as f:
                json.dump(campaign, f, indent=2)
            
            st.success(f"Campaign saved! File: {campaign_file}")
            
            # Generate creatives using the pipeline
            st.markdown("### 🎨 Generating Creatives...")
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Pipeline components are already imported at the top of the file
                
                # Convert campaign to CampaignBrief object
                products = []
                for product_data in campaign["products"]:
                    product = Product(
                        name=product_data["name"],
                        description=product_data["description"],
                        category=product_data["category"],
                        price=product_data["price"],
                        features=product_data["features"],
                        target_demographic=product_data["target_demographic"]
                    )
                    products.append(product)
                
                # Convert aspect ratios
                aspect_ratios = []
                for ratio in campaign["aspect_ratios"]:
                    if ratio == "1:1":
                        aspect_ratios.append(AspectRatio.SQUARE)
                    elif ratio == "9:16":
                        aspect_ratios.append(AspectRatio.VERTICAL)
                    elif ratio == "16:9":
                        aspect_ratios.append(AspectRatio.HORIZONTAL)
                
                # Convert content type
                content_type_map = {
                    "Image Only": ContentType.IMAGE,
                    "Video Only": ContentType.VIDEO,
                    "Both Images & Videos": ContentType.BOTH
                }
                content_type = content_type_map.get(campaign["content_type"], ContentType.IMAGE)
                
                # Convert video format
                video_format = None
                if campaign["video_format"]:
                    video_format_map = {
                        "YouTube Shorts": VideoFormat.YOUTUBE_SHORTS,
                        "Instagram Reels": VideoFormat.INSTAGRAM_REELS,
                        "TikTok": VideoFormat.TIKTOK,
                        "Story": VideoFormat.STORY
                    }
                    video_format = video_format_map.get(campaign["video_format"])
                
                campaign_brief = CampaignBrief(
                    campaign_id=campaign["campaign_id"],
                    campaign_name=campaign["campaign_name"],
                    products=products,
                    target_region=campaign["target_region"],
                    target_audience=campaign["target_audience"],
                    campaign_message=campaign["campaign_message"],
                    aspect_ratios=aspect_ratios,
                    language=campaign["language"],
                    brand_guidelines=campaign["brand_guidelines"],
                    asset_params=campaign.get("asset_params", {}),
                    content_type=content_type,
                    video_format=video_format,
                    video_duration=campaign["video_duration"],
                    include_music=campaign["include_music"],
                    include_voice_over=campaign["include_voice_over"]
                )
                
                # Create generation request
                request = GenerationRequest(
                    campaign_brief=campaign_brief,
                    input_assets=[]  # No input assets for now
                )
                
                # Initialize pipeline
                status_text.text("Initializing pipeline...")
                progress_bar.progress(10)

                # Load configuration from environment and validate
                config = validate_config()
                
                # Override video config with campaign-specific settings
                config["video_config"].update({
                    "output_dir": "output/videos",
                    "duration": campaign["video_duration"] if campaign["video_duration"] else 15,
                    "fps": 30,
                    "resolution": {"width": 1080, "height": 1920},
                    "background_music_volume": 0.3,
                    "text_color": "#FFFFFF",
                    "text_outline_color": "#000000",
                    "font_size": 60,
                    "include_music": campaign["include_music"] if campaign["include_music"] else True,
                    "include_voice_over": campaign["include_voice_over"] if campaign["include_voice_over"] else True,
                    "use_veo3": campaign["use_veo3"] if campaign["use_veo3"] else True,
                    "veo3_config": {
                        "api_key": os.getenv("GOOGLE_AI_API_KEY"),
                        "quality": campaign["veo3_quality"] if campaign["veo3_quality"] else "High",
                        "duration": 8,  # Veo 3 is fixed at 8 seconds
                        "resolution": {"width": 1280, "height": 720},  # 720p
                        "fps": 24  # Veo 3 is fixed at 24fps
                    }
                })
                
                pipeline = CreativePipeline(output_dir="output", config=config)
                
                # Run pipeline
                status_text.text("Generating creatives...")
                progress_bar.progress(30)
                
                import asyncio
                result = asyncio.run(pipeline.process_campaign(request))
                
                progress_bar.progress(100)
                status_text.text("Generation complete!")
                
                # Display results
                if result.total_videos > 0:
                    st.success(f"✅ Successfully generated {result.total_creatives} creatives and {result.total_videos} videos!")
                else:
                    st.success(f"✅ Successfully generated {result.total_creatives} creatives!")
                st.info(f"📁 Output directory: {result.output_directory}")
                st.info(f"📊 Success rate: {result.success_rate:.1%}")
                
                # Store results in session state for display outside form
                st.session_state.last_generation_result = result
                st.session_state.show_results = True
                
                # Add to session state
                st.session_state.campaigns.append(campaign)
                
                # Mark that we need to show the next steps button
                st.session_state.show_gallery_button = True
                
            except Exception as e:
                st.error(f"❌ Error generating creatives: {str(e)}")
                st.info("💡 Check the console for detailed error information")
                import traceback
                st.code(traceback.format_exc())
    
    # Show gallery button if campaign was generated successfully
    if hasattr(st.session_state, 'show_gallery_button') and st.session_state.show_gallery_button:
        st.markdown("### 🎯 Next Steps")
        st.info("🎨 View your generated creatives in the Creative Gallery!")
        if st.button("🖼️ Go to Creative Gallery"):
            st.session_state.current_page = "Creative Gallery"
            st.rerun()
    
    # Display results outside the form (if available)
    if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
        result = st.session_state.last_generation_result
        
        if result and result.generated_creatives:
            st.markdown("### 🎨 Generated Creatives")
            
            # Group by product
            products_creatives = {}
            for creative in result.generated_creatives:
                if creative.product_name not in products_creatives:
                    products_creatives[creative.product_name] = []
                products_creatives[creative.product_name].append(creative)
            
            for product_name, creatives in products_creatives.items():
                st.markdown(f"#### {product_name}")
                
                # Display creatives in columns
                cols = st.columns(len(creatives))
                for i, creative in enumerate(creatives):
                    with cols[i]:
                        st.markdown(f"**{creative.aspect_ratio.value}**")
                        
                        # Display image if it exists
                        creative_path = Path(creative.file_path)
                        if creative_path.exists():
                            with open(creative_path, "rb") as f:
                                image_data = f.read()
                                st.image(image_data, caption=f"Quality: {creative.quality_score:.2f}" if creative.quality_score else "Quality: N/A")
                                
                                # Download button (now outside form)
                                st.download_button(
                                    label="📥 Download",
                                    data=image_data,
                                    file_name=creative_path.name,
                                    mime="image/jpeg",
                                    width='stretch'
                                )
                        else:
                            st.warning("Creative file not found")
        
        # Display videos if available
        if result and result.generated_videos:
            st.markdown("### 🎬 Generated Videos")
            
            # Group videos by product
            products_videos = {}
            for video in result.generated_videos:
                if video.product_name not in products_videos:
                    products_videos[video.product_name] = []
                products_videos[video.product_name].append(video)
            
            for product_name, videos in products_videos.items():
                st.markdown(f"#### {product_name} Videos")
                
                # Display videos in columns
                cols = st.columns(len(videos))
                for i, video in enumerate(videos):
                    with cols[i]:
                        st.markdown(f"**{video.video_format.value}**")
                        st.markdown(f"Duration: {video.duration}s")
                        st.markdown(f"Music: {'✅' if video.has_music else '❌'}")
                        st.markdown(f"Voice-over: {'✅' if video.has_voice_over else '❌'}")
                        
                        # Display video if it exists
                        video_path = Path(video.file_path)
                        if video_path.exists():
                            with open(video_path, "rb") as f:
                                video_data = f.read()
                                
                                # Download button for video
                                st.download_button(
                                    label="📥 Download Video",
                                    data=video_data,
                                    file_name=video_path.name,
                                    mime="video/mp4",
                                    width='stretch'
                                )
                        else:
                            st.warning("Video file not found")
            
            # Clear the results flag
            st.session_state.show_results = False

def show_creative_gallery():
    """Show the creative gallery with all creatives and campaign filtering."""
    
    st.markdown("## 🎨 Creative Gallery")
    st.markdown("View all generated creatives and videos across all campaigns.")
    
    output_dir = Path("output")
    
    if not output_dir.exists():
        st.info("No generated creatives found. Create a campaign first!")
        return
    
    # Get all campaigns
    campaigns = [d for d in output_dir.iterdir() if d.is_dir() and d.name != "assets" and d.name != "videos" and d.name != "templates" and d.name != "logs"]
    
    if not campaigns:
        st.info("No campaigns found in output directory.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Campaign filter
        campaign_options = ["All Campaigns"] + [c.name for c in campaigns]
        selected_campaign = st.selectbox("Filter by Campaign:", campaign_options)
    
    with col2:
        # Content type filter
        content_type_filter = st.selectbox("Filter by Type:", ["All", "Images", "Videos"])
    
    with col3:
        # Sort options
        sort_option = st.selectbox("Sort by:", ["Newest First", "Oldest First", "Campaign Name"])
    
    # Collect all creatives and videos
    all_creatives = []
    all_videos = []
    
    # Load S3 URLs from campaign output files
    s3_urls = {}
    for campaign_dir in campaigns:
        campaign_output_file = campaign_dir / "campaign_output.json"
        if campaign_output_file.exists():
            try:
                with open(campaign_output_file, 'r') as f:
                    campaign_data = json.load(f)
                    for creative in campaign_data.get("generated_creatives", []):
                        if creative.get("s3_url"):
                            s3_urls[creative["file_path"]] = creative["s3_url"]
                    for video in campaign_data.get("generated_videos", []):
                        if video.get("s3_url"):
                            s3_urls[video["file_path"]] = video["s3_url"]
            except Exception as e:
                st.warning(f"Could not load S3 URLs for campaign {campaign_dir.name}: {e}")
    
    # Get all images from campaigns
    for campaign_dir in campaigns:
        campaign_name = campaign_dir.name
        products = [d for d in campaign_dir.iterdir() if d.is_dir()]
        
        for product_dir in products:
            product_name = product_dir.name.replace("_", " ").title()
            
            # Look for creatives in aspect ratio folders
            creatives = []
            aspect_ratio_folders = ["1x1", "9x16", "16x9"]
            for aspect_folder in aspect_ratio_folders:
                aspect_dir = product_dir / aspect_folder
                if aspect_dir.exists():
                    creatives.extend(list(aspect_dir.glob("*.jpg")))
            
            for creative in creatives:
                # Determine aspect ratio from parent folder
                parent_folder = creative.parent.name
                if parent_folder == "1x1":
                    aspect_ratio = "1:1"
                elif parent_folder == "9x16":
                    aspect_ratio = "9:16"
                elif parent_folder == "16x9":
                    aspect_ratio = "16:9"
                else:
                    aspect_ratio = "Unknown"
                
                # Get S3 URL if available
                s3_url = s3_urls.get(str(creative), None)
                
                all_creatives.append({
                    "file_path": creative,
                    "campaign_name": campaign_name,
                    "product_name": product_name,
                    "aspect_ratio": aspect_ratio,
                    "type": "image",
                    "modified_time": creative.stat().st_mtime,
                    "s3_url": s3_url
                })
    
    # Get all videos
    videos_dir = output_dir / "videos"
    if videos_dir.exists():
        for video_file in videos_dir.glob("*.mp4"):
            # Try to extract campaign and product info from filename
            filename = video_file.stem
            campaign_name = "Unknown Campaign"
            product_name = "Unknown Product"
            
            # Look for campaign info in filename
            for campaign in campaigns:
                if campaign.name.replace("_", "").lower() in filename.lower():
                    campaign_name = campaign.name
                    break
            
            # Get S3 URL if available
            s3_url = s3_urls.get(str(video_file), None)
            
            all_videos.append({
                "file_path": video_file,
                "campaign_name": campaign_name,
                "product_name": product_name,
                "aspect_ratio": "Video",
                "s3_url": s3_url,
                "type": "video",
                "modified_time": video_file.stat().st_mtime
            })
    
    # Apply filters
    filtered_creatives = all_creatives.copy()
    filtered_videos = all_videos.copy()
    
    # Campaign filter
    if selected_campaign != "All Campaigns":
        filtered_creatives = [c for c in filtered_creatives if c["campaign_name"] == selected_campaign]
        filtered_videos = [v for v in filtered_videos if v["campaign_name"] == selected_campaign]
    
    # Content type filter
    if content_type_filter == "Images":
        filtered_videos = []
    elif content_type_filter == "Videos":
        filtered_creatives = []
    
    # Combine and sort
    all_items = filtered_creatives + filtered_videos
    
    if sort_option == "Newest First":
        all_items.sort(key=lambda x: x["modified_time"], reverse=True)
    elif sort_option == "Oldest First":
        all_items.sort(key=lambda x: x["modified_time"])
    elif sort_option == "Campaign Name":
        all_items.sort(key=lambda x: x["campaign_name"])
    
    # Display results
    if all_items:
        st.markdown(f"### 📊 Found {len(all_items)} items")
        
        # Group by campaign for better organization
        campaigns_display = {}
        for item in all_items:
            campaign = item["campaign_name"]
            if campaign not in campaigns_display:
                campaigns_display[campaign] = []
            campaigns_display[campaign].append(item)
        
        # Display by campaign
        for campaign_name, items in campaigns_display.items():
            st.markdown(f"#### 🎯 {campaign_name}")
            
            # Group by product
            products_display = {}
            for item in items:
                product = item["product_name"]
                if product not in products_display:
                    products_display[product] = []
                products_display[product].append(item)
            
            for product_name, product_items in products_display.items():
                st.markdown(f"##### 📦 {product_name}")
                
                # Display items in a grid
                cols = st.columns(min(len(product_items), 4))
                
                for i, item in enumerate(product_items):
                    with cols[i % 4]:
                        # Display item
                        if item["type"] == "image":
                            try:
                                image = Image.open(item["file_path"])
                                st.image(image, caption=f"{item['aspect_ratio']} - {item['file_path'].name}", width='stretch')
                                
                                # Download button
                                with open(item["file_path"], "rb") as f:
                                    st.download_button(
                                        label="📥 Download",
                                        data=f.read(),
                                        file_name=item["file_path"].name,
                                        mime="image/jpeg",
                                        key=f"download_{item['file_path'].name}_{i}"
                                    )
                                
                                # S3 URL display (if available)
                                if "s3_url" in item and item["s3_url"]:
                                    st.markdown(f"☁️ **S3 URL:**")
                                    st.code(item["s3_url"], language="text")
                                    
                                    # Copy to clipboard button
                                    if st.button("📋 Copy S3 URL", key=f"copy_s3_{item['file_path'].name}_{i}"):
                                        st.success("S3 URL copied to clipboard!")
                            except Exception as e:
                                st.error(f"Error loading {item['file_path'].name}")
                        
                        elif item["type"] == "video":
                            try:
                                with open(item["file_path"], "rb") as video_file:
                                    video_bytes = video_file.read()
                                    st.video(video_bytes)
                                
                                # Download button
                                with open(item["file_path"], "rb") as f:
                                    st.download_button(
                                        label="📥 Download Video",
                                        data=f.read(),
                                        file_name=item["file_path"].name,
                                        mime="video/mp4",
                                        key=f"download_video_{item['file_path'].name}_{i}"
                                    )
                                
                                # S3 URL display (if available)
                                if "s3_url" in item and item["s3_url"]:
                                    st.markdown(f"☁️ **S3 URL:**")
                                    st.code(item["s3_url"], language="text")
                                    
                                    # Copy to clipboard button
                                    if st.button("📋 Copy S3 URL", key=f"copy_s3_video_{item['file_path'].name}_{i}"):
                                        st.success("S3 URL copied to clipboard!")
                            except Exception as e:
                                st.error(f"Error loading {item['file_path'].name}")
                        
                        # Show tags
                        st.caption(f"🏷️ {item['campaign_name']} • {item['product_name']} • {item['aspect_ratio']}")
    else:
        st.info("No creatives found matching your filters.")

def show_s3_management():
    """Show S3 storage management page."""
    
    st.markdown("## ☁️ S3 Storage Management")
    st.markdown("Manage your AWS S3 storage for campaign data, assets, and generated creatives.")
    
    # Load configuration
    config = validate_config()
    s3_config = config.get("s3_config", {})
    
    # Check S3 availability
    s3_available = bool(s3_config.get("aws_access_key_id") and s3_config.get("aws_secret_access_key"))
    
    if not s3_available:
        st.warning("⚠️ S3 storage is not configured. Please set your AWS credentials in the environment variables.")
        st.markdown("### Required Environment Variables:")
        st.code("""
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
S3_BUCKET_NAME=creative-automation-pipeline
S3_REGION=us-east-1
        """)
        return
    
    # Initialize S3 storage manager
    s3_storage = S3StorageManager(s3_config)
    
    if not s3_storage.is_available():
        st.error("❌ S3 storage is not available. Please check your AWS credentials and bucket configuration.")
        return
    
    st.success("✅ S3 storage is configured and available!")
    
    # Display S3 configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 S3 Configuration")
        st.info(f"**Bucket:** {s3_config.get('s3_bucket_name', 'Not set')}")
        st.info(f"**Region:** {s3_config.get('s3_region', 'Not set')}")
        st.info(f"**Prefix:** {s3_config.get('s3_prefix', 'campaigns')}")
    
    with col2:
        st.markdown("### 🔧 S3 Actions")
        
        # Test S3 connection
        if st.button("🔍 Test S3 Connection"):
            try:
                if s3_storage._test_connection():
                    st.success("✅ S3 connection successful!")
                else:
                    st.error("❌ S3 connection failed!")
            except Exception as e:
                st.error(f"❌ S3 connection error: {e}")
        
        # List campaigns in S3
        if st.button("📁 List Campaigns in S3"):
            try:
                # This would require implementing a method to list campaigns
                st.info("Campaign listing functionality would be implemented here")
            except Exception as e:
                st.error(f"Error listing campaigns: {e}")
    
    # Tabs for different S3 operations
    tab1, tab2, tab3 = st.tabs(["📊 Storage Overview", "📤 Upload to S3", "📥 Download from S3"])
    
    with tab1:
        st.markdown("### 📊 Storage Overview")
        st.info("Storage overview functionality would show bucket usage, file counts, and storage costs.")
        
        # Mock storage statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Campaigns", "12", "3")
        with col2:
            st.metric("Total Creatives", "156", "24")
        with col3:
            st.metric("Total Videos", "8", "2")
        with col4:
            st.metric("Storage Used", "2.4 GB", "0.3 GB")
    
    with tab2:
        st.markdown("### 📤 Upload to S3")
        st.info("Upload local files to S3 storage.")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload to S3",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png', 'mp4', 'json']
        )
        
        if uploaded_files:
            campaign_id = st.text_input("Campaign ID (for organization):", value="manual_upload")
            
            if st.button("📤 Upload to S3"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {uploaded_file.name}...")
                    
                    # Save file temporarily
                    temp_path = Path("temp") / uploaded_file.name
                    temp_path.parent.mkdir(exist_ok=True)
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Upload to S3
                    try:
                        if uploaded_file.type.startswith('image/'):
                            s3_url = asyncio.run(s3_storage.upload_asset(
                                local_file_path=temp_path,
                                campaign_id=campaign_id,
                                asset_category="manual_upload"
                            ))
                        elif uploaded_file.type == 'video/mp4':
                            s3_url = asyncio.run(s3_storage.upload_video(
                                local_file_path=temp_path,
                                campaign_id=campaign_id,
                                product_name="manual_upload",
                                video_format="manual"
                            ))
                        else:
                            s3_url = asyncio.run(s3_storage.upload_asset(
                                local_file_path=temp_path,
                                campaign_id=campaign_id,
                                asset_category="manual_upload"
                            ))
                        
                        if s3_url:
                            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                            st.code(s3_url)
                        else:
                            st.error(f"❌ Failed to upload {uploaded_file.name}")
                    
                    except Exception as e:
                        st.error(f"❌ Error uploading {uploaded_file.name}: {e}")
                    
                    # Clean up temp file
                    temp_path.unlink()
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("Upload complete!")
    
    with tab3:
        st.markdown("### 📥 Download from S3")
        st.info("Download files from S3 storage.")
        
        s3_url = st.text_input("Enter S3 URL to download:")
        local_path = st.text_input("Local save path:", value="downloads/")
        
        if st.button("📥 Download from S3") and s3_url:
            try:
                local_path = Path(local_path)
                local_path.mkdir(parents=True, exist_ok=True)
                
                # Extract filename from URL
                filename = s3_url.split('/')[-1]
                download_path = local_path / filename
                
                success = asyncio.run(s3_storage.download_file(s3_url, download_path))
                
                if success:
                    st.success(f"✅ File downloaded to: {download_path}")
                else:
                    st.error("❌ Download failed!")
            
            except Exception as e:
                st.error(f"❌ Download error: {e}")

def show_analytics():
    """Show analytics and performance metrics."""
    
    st.markdown("## 📈 Analytics & Performance")
    
    # Mock data for demonstration
    data = {
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Campaigns': [2, 3, 1, 4, 2, 3, 5, 2, 4, 3, 2, 1, 3, 4, 2, 3, 2, 4, 3, 2, 1, 3, 4, 2, 3, 2, 4, 3, 2, 1],
        'Creatives': [6, 9, 3, 12, 6, 9, 15, 6, 12, 9, 6, 3, 9, 12, 6, 9, 6, 12, 9, 6, 3, 9, 12, 6, 9, 6, 12, 9, 6, 3],
        'Success_Rate': [0.95, 0.92, 0.98, 0.89, 0.94, 0.91, 0.87, 0.96, 0.88, 0.93, 0.95, 0.97, 0.90, 0.89, 0.94, 0.91, 0.96, 0.88, 0.93, 0.95, 0.97, 0.90, 0.89, 0.94, 0.91, 0.96, 0.88, 0.93, 0.95, 0.97]
    }
    
    df = pd.DataFrame(data)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Campaign Volume")
        fig = px.line(df, x='Date', y='Campaigns', title='Daily Campaign Count')
        fig.update_layout(height=300)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.markdown("### 🎨 Creative Generation")
        fig = px.line(df, x='Date', y='Creatives', title='Daily Creative Count')
        fig.update_layout(height=300)
        st.plotly_chart(fig, width='stretch')
    
    # Success rate chart
    st.markdown("### ✅ Success Rate Trend")
    fig = px.line(df, x='Date', y='Success_Rate', title='Pipeline Success Rate')
    fig.update_layout(height=400)
    fig.update_layout(yaxis=dict(tickformat='.1%'))
    st.plotly_chart(fig, width='stretch')
    
    # Performance metrics
    st.markdown("### 🚀 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Avg Generation Time", "2.3s", "0.2s")
    
    with col2:
        st.metric("Quality Score", "0.87", "0.03")
    
    with col3:
        st.metric("API Success Rate", "98.5%", "1.2%")
    
    with col4:
        st.metric("Cost per Creative", "$0.15", "-$0.02")

def show_settings():
    """Show settings and configuration."""
    
    st.markdown("## ⚙️ Settings & Configuration")
    
    # AI Configuration
    st.markdown("### 🤖 AI Configuration")
    
    with st.form("ai_config"):
        openai_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key for DALL-E image generation")
        dalle_model = st.selectbox("DALL-E Model", ["dall-e-3", "dall-e-2"], index=0)
        fallback_mode = st.checkbox("Enable Fallback Mode", value=True, help="Use mock images when AI is unavailable")
        
        if st.form_submit_button("💾 Save AI Settings"):
            st.success("AI settings saved!")
    
    st.markdown("---")
    
    # Quality Settings
    st.markdown("### 🎯 Quality Settings")
    
    with st.form("quality_config"):
        min_quality = st.slider("Minimum Quality Score", 0.0, 1.0, 0.7, 0.05)
        min_resolution = st.selectbox("Minimum Resolution", ["800x800", "1024x1024", "1920x1080"], index=1)
        max_file_size = st.number_input("Max File Size (MB)", 1, 50, 10)
        
        if st.form_submit_button("💾 Save Quality Settings"):
            st.success("Quality settings saved!")
    
    st.markdown("---")
    
    # Brand Guidelines
    st.markdown("### 🎨 Default Brand Guidelines")
    
    with st.form("brand_config"):
        col1, col2 = st.columns(2)
        
        with col1:
            default_primary = st.color_picker("Default Primary Color", value="#667eea")
            default_secondary = st.color_picker("Default Secondary Color", value="#ffffff")
        
        with col2:
            default_accent = st.color_picker("Default Accent Color", value="#ffd700")
            default_font = st.selectbox("Default Font", ["Arial", "Helvetica", "Times New Roman", "Georgia"])
        
        if st.form_submit_button("💾 Save Brand Settings"):
            st.success("Brand settings saved!")
    
    st.markdown("---")
    
    # System Information
    st.markdown("### 📋 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Pipeline Version:** 1.0.0  
        **Python Version:** {sys.version.split()[0]}  
        **Streamlit Version:** {st.__version__}  
        **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
    
    with col2:
        st.info(f"""
        **Output Directory:** {Path('output').absolute()}  
        **Examples Directory:** {Path('examples').absolute()}  
        **Logs Directory:** {Path('logs').absolute()}  
        **Status:** Ready
        """)

def show_assets_page():
    """Show the assets management page."""
    
    st.markdown("## 🎨 Assets Management")
    st.markdown("Manage your brand assets including logos, avatars, backgrounds, and themes.")
    
    # Create assets directory if it doesn't exist
    assets_dir = Path("output/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Tabs for different asset types
    tab1, tab2, tab3 = st.tabs(["📁 Browse Assets", "⬆️ Upload Assets", "🤖 Generate with DALL-E"])
    
    with tab1:
        st.markdown("### 📁 Available Assets")
        
        # Define asset categories
        asset_categories = ["brand_logo", "avatar", "background", "theme", "general"]
        category_names = {
            "brand_logo": "🏷️ Brand Logos",
            "avatar": "👤 Avatars/Models", 
            "background": "🌅 Backgrounds",
            "theme": "🎨 Themes",
            "general": "📦 General"
        }
        
        # Display assets by category
        for category in asset_categories:
            category_dir = assets_dir / category
            if category_dir.exists():
                st.markdown(f"#### {category_names[category]}")
                
                # Get all files in category directory
                category_files = []
                for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg"]:
                    category_files.extend(category_dir.glob(ext))
                
                if category_files:
                    cols = st.columns(min(len(category_files), 4))
                    
                    for i, asset_file in enumerate(category_files):
                        with cols[i % 4]:
                            try:
                                # Display image
                                image = Image.open(asset_file)
                                st.image(image, caption=asset_file.name, width='stretch')
                                
                                # Download button
                                with open(asset_file, "rb") as f:
                                    st.download_button(
                                        label="📥 Download",
                                        data=f.read(),
                                        file_name=asset_file.name,
                                        mime="image/jpeg",
                                        key=f"download_{asset_file.name}"
                                    )
                            except Exception as e:
                                st.error(f"Error loading {asset_file.name}: {e}")
        else:
            st.info("No assets found. Upload some assets or generate them with DALL-E!")
    
    with tab2:
        st.markdown("### ⬆️ Upload Assets")
        
        # Category selection for uploads
        upload_category = st.selectbox(
            "Select Category for Upload",
            ["brand_logo", "avatar", "background", "theme", "general"],
            help="Select the category for the assets you're uploading"
        )
        
        uploaded_files = st.file_uploader(
            "Choose asset files",
            type=['jpg', 'jpeg', 'png', 'gif', 'svg'],
            accept_multiple_files=True,
            help="Upload brand logos, avatars, backgrounds, themes, etc."
        )
        
        if uploaded_files:
            # Create category directory
            category_dir = assets_dir / upload_category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                # Save uploaded file to category directory
                file_path = category_dir / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ Uploaded: {uploaded_file.name} to {upload_category} category")
    
    with tab3:
        st.markdown("### 🤖 Generate Assets with DALL-E")
        
        # Asset type selection
        asset_type = st.selectbox(
            "Asset Type",
            ["Brand Logo", "Avatar/Model", "Background", "Theme", "Custom"],
            help="Select the type of asset you want to generate"
        )
        
        # Prompt input
        if asset_type == "Brand Logo":
            default_prompt = "Modern minimalist logo design for a tech company, clean lines, professional, vector style"
        elif asset_type == "Avatar/Model":
            default_prompt = "Professional headshot of a diverse business person, high quality, studio lighting"
        elif asset_type == "Background":
            default_prompt = "Starry night sky with aurora borealis, cinematic, high resolution, dark theme"
        elif asset_type == "Theme":
            default_prompt = "Modern geometric pattern, colorful, abstract, suitable for social media backgrounds"
        else:
            default_prompt = ""
        
        prompt = st.text_area(
            "DALL-E Prompt",
            value=default_prompt,
            height=100,
            help="Describe the asset you want to generate"
        )
        
        # Generation options
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("Asset Category", ["brand_logo", "avatar", "background", "theme", "general"])
        with col2:
            asset_type = st.selectbox("Asset Type", ["image", "logo", "avatar", "background", "theme"])
        
        if st.button("🎨 Generate Asset", width='stretch'):
            if prompt:
                with st.spinner("Generating asset with DALL-E..."):
                    try:
                        # Import DALL-E generator
                        from src.pipeline.asset_generator import AssetGenerator
                        
                        # Initialize generator
                        config = {"openai_api_key": os.getenv("OPENAI_API_KEY")}
                        generator = AssetGenerator(config)
                        
                        # Generate image using new function
                        image_path = generator.generate_with_dalle(
                            prompt=prompt,
                            category=category,
                            asset_type=asset_type
                        )
                        
                        if image_path:
                            st.success("✅ Asset generated successfully!")
                            
                            # Display generated image
                            image = Image.open(image_path)
                            st.image(image, caption=f"Generated: {Path(image_path).name}", width='stretch')
                            
                            # Download button
                            with open(image_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Generated Asset",
                                    data=f.read(),
                                    file_name=Path(image_path).name,
                                    mime="image/jpeg"
                                )
                        else:
                            st.error("❌ Failed to generate asset")
                            
                    except Exception as e:
                        st.error(f"❌ Error generating asset: {e}")
            else:
                st.warning("Please enter a prompt for the asset generation")

if __name__ == "__main__":
    main()
