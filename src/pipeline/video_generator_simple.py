"""
Simple video generation component that creates mock videos without MoviePy dependency.
This is a temporary solution to avoid the .env file corruption issue.
"""

import asyncio
import os
import random
from pathlib import Path
from typing import List, Optional, Dict, Any
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
import json

try:
    from .models import Product, CampaignBrief, AspectRatio
    from .google_veo3_generator import GoogleVeo3Generator
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import Product, CampaignBrief, AspectRatio
    from google_veo3_generator import GoogleVeo3Generator

from loguru import logger


class VideoGenerator:
    """Simple video generator that creates mock videos without MoviePy."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "output/videos"))
        self.video_duration = config.get("duration", 15)
        self.fps = config.get("fps", 24)
        self.resolution = config.get("resolution", (720, 1280))  # 9:16 for mobile
        self.include_music = config.get("music", True)
        self.include_voice = config.get("voice_enabled", True)
        self.use_veo3 = config.get("use_veo3", False)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Google Veo 3 generator if enabled
        self.veo3_generator = None
        if self.use_veo3:
            try:
                veo3_config = config.get("veo3_config", {})
                self.veo3_generator = GoogleVeo3Generator(veo3_config)
                logger.info("Google Veo 3 generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Veo 3: {e}")
                self.use_veo3 = False
        
        logger.info(f"VideoGenerator initialized: duration={self.video_duration}s, fps={self.fps}, resolution={self.resolution}")
    
    async def generate_video_ad(self, product: Product, campaign_brief: CampaignBrief, product_images: List[str] = None, output_filename: str = None) -> Optional[str]:
        """Generate a video advertisement for a product."""
        try:
            logger.info(f"Generating video ad for product: {product.name}")
            
            # Try Google Veo 3 first if enabled
            if self.use_veo3 and self.veo3_generator:
                try:
                    video_path = await self.veo3_generator.generate_video_ad(product, campaign_brief)
                    if video_path and Path(video_path).exists():
                        logger.info(f"Google Veo 3 video generated: {video_path}")
                        return video_path
                except Exception as e:
                    logger.warning(f"Google Veo 3 generation failed: {e}")
            
            # Fallback to simple mock video generation
            return await self._create_mock_video(product, campaign_brief, output_filename)
            
        except Exception as e:
            logger.error(f"Error generating video ad: {e}")
            return None
    
    async def _create_mock_video(self, product: Product, campaign_brief: CampaignBrief, output_filename: str = None) -> str:
        """Create a simple mock video using OpenCV."""
        try:
            # Create video filename
            if output_filename:
                video_filename = output_filename
            else:
                video_filename = f"{product.name.replace(' ', '_').lower()}_video.mp4"
            video_path = self.output_dir / video_filename
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(video_path), fourcc, self.fps, self.resolution)
            
            # Generate frames
            total_frames = int(self.video_duration * self.fps)
            
            for frame_num in range(total_frames):
                # Create frame with product information
                frame = self._create_frame(product, campaign_brief, frame_num, total_frames)
                out.write(frame)
            
            out.release()
            logger.info(f"Mock video created: {video_path}")
            return str(video_path)
            
        except Exception as e:
            logger.error(f"Error creating mock video: {e}")
            return None
    
    def _create_frame(self, product: Product, campaign_brief: CampaignBrief, frame_num: int, total_frames: int) -> np.ndarray:
        """Create a single frame for the video."""
        # Create a colored background
        frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Add gradient background
        for y in range(self.resolution[1]):
            color_value = int(50 + (y / self.resolution[1]) * 100)
            frame[y, :] = [color_value, color_value + 20, color_value + 40]
        
        # Convert to PIL for text rendering
        pil_frame = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_frame)
        
        # Try to load a font
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add product name
        product_text = product.name
        bbox = draw.textbbox((0, 0), product_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.resolution[0] - text_width) // 2
        draw.text((text_x, 200), product_text, fill=(255, 255, 255), font=font_large)
        
        # Add campaign message
        message_text = campaign_brief.campaign_message
        bbox = draw.textbbox((0, 0), message_text, font=font_medium)
        text_width = bbox[2] - bbox[0]
        text_x = (self.resolution[0] - text_width) // 2
        draw.text((text_x, 300), message_text, fill=(255, 255, 255), font=font_medium)
        
        # Add price if available
        if hasattr(product, 'price') and product.price:
            price_text = f"${product.price}"
            bbox = draw.textbbox((0, 0), price_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_x = (self.resolution[0] - text_width) // 2
            draw.text((text_x, 400), price_text, fill=(0, 255, 0), font=font_large)
        
        # Add animated element (simple moving circle)
        progress = frame_num / total_frames
        circle_x = int(100 + progress * (self.resolution[0] - 200))
        circle_y = self.resolution[1] - 150
        draw.ellipse([circle_x-20, circle_y-20, circle_x+20, circle_y+20], fill=(255, 0, 0))
        
        # Convert back to OpenCV format
        frame = np.array(pil_frame)
        return frame
    
    def _get_product_images(self, product: Product) -> List[str]:
        """Get product images from the assets directory."""
        try:
            assets_dir = Path("output/assets")
            if not assets_dir.exists():
                return []
            
            # Look for images related to this product
            product_name = product.name.replace(" ", "_").lower()
            image_files = []
            
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                image_files.extend(assets_dir.glob(f"**/{product_name}*{ext}"))
            
            return [str(img) for img in image_files[:5]]  # Limit to 5 images
            
        except Exception as e:
            logger.error(f"Error getting product images: {e}")
            return []
