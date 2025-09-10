"""
Google Veo 3 video generation component for creating high-quality video advertisements.
"""

import asyncio
import os
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
import base64
from datetime import datetime

try:
    from .models import Product, CampaignBrief, VideoFormat
    from google import genai
    from google.genai import types
except ImportError:
    from models import Product, CampaignBrief, VideoFormat
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        genai = None
        types = None


class GoogleVeo3Generator:
    """Generates high-quality videos using Google Veo 3 API."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Google Veo 3 generator.
        
        Args:
            config: Configuration dictionary for Veo 3 settings
        """
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.getenv("GOOGLE_AI_API_KEY")
        
        # Video settings
        self.output_dir = Path(self.config.get("output_dir", "output/videos"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default video parameters (Veo 3 generates 8-second 720p videos)
        self.default_duration = 8  # Veo 3 is fixed at 8 seconds
        self.default_resolution = {"width": 1280, "height": 720}  # 720p
        self.default_fps = 24  # Veo 3 is fixed at 24fps
        
        # Initialize Google AI client
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Google AI client: {e}")
                self.client = None
        
    async def generate_video_ad(
        self,
        product: Product,
        campaign_brief: CampaignBrief,
        product_images: List[str] = None,
        output_filename: str = None
    ) -> str:
        """Generate a video advertisement using Google Veo 3.
        
        Args:
            product: Product information
            campaign_brief: Campaign brief with messaging
            product_images: List of product image paths (optional)
            output_filename: Output video filename
            
        Returns:
            Path to the generated video file
        """
        try:
            if not self.client or not self.api_key:
                print("Warning: No Google AI API key or client found. Using mock video generation.")
                return await self._create_mock_video(product, campaign_brief, output_filename)
            
            # Create video prompt
            video_prompt = self._create_veo3_prompt(product, campaign_brief)
            
            # Generate video using Veo 3
            video_path = await self._call_veo3_api(video_prompt, product_images, output_filename)
            
            if video_path and Path(video_path).exists():
                return str(video_path)
            else:
                print("Failed to generate video with Veo 3. Using mock video.")
                return await self._create_mock_video(product, campaign_brief, output_filename)
                
        except Exception as e:
            print(f"Error generating video with Veo 3: {e}")
            return await self._create_mock_video(product, campaign_brief, output_filename)
    
    def _create_veo3_prompt(self, product: Product, campaign_brief: CampaignBrief) -> str:
        """Create a detailed prompt for Veo 3 video generation following best practices."""
        
        # Subject: The main focus of the video
        subject = f"{product.name}"
        if product.description:
            subject += f" - {product.description}"
        
        # Action: What the product is doing or how it's being showcased
        action = "being showcased in a professional advertisement"
        
        # Style: Commercial/cinematic style
        style = "cinematic commercial style, professional lighting, modern aesthetic"
        
        # Camera positioning and motion
        camera_motion = "smooth camera movements, close-up shots transitioning to wide shots"
        
        # Composition
        composition = "dynamic composition with multiple angles"
        
        # Ambiance
        ambiance = "warm, inviting lighting with professional studio setup"
        
        # Build the main prompt
        prompt = f"A {composition} of {subject} {action} in {style}. {camera_motion}. {ambiance}."
        
        # Add specific details
        if product.category:
            prompt += f" The product is in the {product.category} category."
        
        if product.features:
            features_text = ", ".join(product.features[:3])  # Limit to 3 features
            prompt += f" Highlighting key features: {features_text}."
        
        # Campaign context
        if campaign_brief.campaign_message:
            prompt += f" The campaign message is: '{campaign_brief.campaign_message}'."
        
        # Brand guidelines
        if campaign_brief.brand_guidelines:
            brand = campaign_brief.brand_guidelines
            if brand.get('primary_color'):
                prompt += f" Use {brand.get('primary_color')} as the primary brand color."
        
        # Target audience
        if campaign_brief.target_audience:
            prompt += f" The video should appeal to {campaign_brief.target_audience}."
        
        # Price display
        if product.price:
            prompt += f" Display the price ${product.price:.2f} prominently."
        
        # Audio cues for Veo 3
        if campaign_brief.include_voice_over and campaign_brief.campaign_message:
            prompt += f" Include voice-over saying: '{campaign_brief.campaign_message}'."
        
        if campaign_brief.include_music:
            prompt += " Include upbeat, modern background music that enhances the product appeal."
        
        # Ensure prompt is within token limit (1024 tokens for Veo 3)
        if len(prompt) > 800:  # Leave some buffer
            prompt = prompt[:800] + "..."
        
        return prompt
    
    async def _call_veo3_api(self, prompt: str, product_images: List[str] = None, output_filename: str = None) -> Optional[str]:
        """Call the Google Veo 3 API to generate video."""
        try:
            if not self.client:
                print("Google AI client not initialized")
                return None
            
            print(f"🎬 Calling Google Veo 3 API with prompt: {prompt[:100]}...")
            
            # Prepare the generation request
            generation_kwargs = {
                "model": "veo-3.0-generate-preview",
                "prompt": prompt,
            }
            
            # Add image if available (for image-to-video generation)
            if product_images and product_images[0] and Path(product_images[0]).exists():
                try:
                    # Load the first product image
                    with open(product_images[0], "rb") as f:
                        image_data = f.read()
                    
                    # Create image object for Veo 3
                    image_obj = types.Image(data=image_data)
                    generation_kwargs["image"] = image_obj
                    print("📸 Using product image as starting frame for video generation")
                except Exception as e:
                    print(f"Warning: Could not load product image: {e}")
            
            # Start the video generation operation
            operation = self.client.models.generate_videos(**generation_kwargs)
            
            print("⏳ Video generation started. This may take 1-6 minutes...")
            
            # Poll the operation status until the video is ready
            while not operation.done:
                print("⏳ Waiting for video generation to complete...")
                await asyncio.sleep(10)  # Wait 10 seconds
                operation = self.client.operations.get(operation)
            
            print("✅ Video generation completed!")
            
            # Download the generated video
            if operation.response and operation.response.generated_videos:
                generated_video = operation.response.generated_videos[0]
                
                # Set output filename if not provided
                if not output_filename:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"veo3_video_{timestamp}.mp4"
                
                output_path = self.output_dir / output_filename
                
                # Download and save the video
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(str(output_path))
                
                print(f"💾 Video saved to: {output_path}")
                return str(output_path)
            else:
                print("❌ No video generated in response")
                return None
                
        except Exception as e:
            print(f"❌ Error calling Veo 3 API: {e}")
            return None
    
    
    async def _create_mock_video(self, product: Product, campaign_brief: CampaignBrief, output_filename: str = None) -> str:
        """Create a mock video for demonstration purposes."""
        try:
            import cv2
            import numpy as np
            
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"mock_video_{timestamp}.mp4"
            
            output_path = self.output_dir / output_filename
            
            # Video parameters (Veo 3 specifications: 8 seconds, 720p, 24fps)
            duration = 8  # Veo 3 is fixed at 8 seconds
            fps = 24  # Veo 3 is fixed at 24fps
            width, height = 1280, 720  # 720p resolution
            total_frames = duration * fps
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Generate frames
            for frame_num in range(total_frames):
                # Create a frame with product information
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Animate background color
                progress = frame_num / total_frames
                color_intensity = int(128 + 127 * np.sin(progress * 2 * np.pi))
                frame[:, :] = [color_intensity // 3, color_intensity // 2, color_intensity]
                
                # Add text overlay
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 2
                color = (255, 255, 255)
                thickness = 3
                
                # Product name
                product_text = product.name
                text_size = cv2.getTextSize(product_text, font, font_scale, thickness)[0]
                text_x = (width - text_size[0]) // 2
                text_y = height // 3
                cv2.putText(frame, product_text, (text_x, text_y), font, font_scale, color, thickness)
                
                # Campaign message
                if campaign_brief.campaign_message:
                    message_text = campaign_brief.campaign_message
                    message_scale = 1
                    message_size = cv2.getTextSize(message_text, font, message_scale, thickness)[0]
                    message_x = (width - message_size[0]) // 2
                    message_y = height // 2
                    cv2.putText(frame, message_text, (message_x, message_y), font, message_scale, color, thickness)
                
                # Price
                if product.price:
                    price_text = f"${product.price:.2f}"
                    price_scale = 1.5
                    price_size = cv2.getTextSize(price_text, font, price_scale, thickness)[0]
                    price_x = (width - price_size[0]) // 2
                    price_y = height * 2 // 3
                    cv2.putText(frame, price_text, (price_x, price_y), font, price_scale, (0, 255, 255), thickness)
                
                # Write frame
                out.write(frame)
            
            # Release video writer
            out.release()
            
            print(f"Mock video created: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"Error creating mock video: {e}")
            # Return a placeholder path
            return str(self.output_dir / (output_filename or "mock_video.mp4"))
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get the status of a video generation job."""
        # This would be implemented to check the status of a Veo 3 generation job
        # For now, return a mock status
        return {
            "video_id": video_id,
            "status": "completed",
            "progress": 100,
            "estimated_time_remaining": 0
        }
    
    def cancel_video_generation(self, video_id: str) -> bool:
        """Cancel a video generation job."""
        # This would be implemented to cancel a Veo 3 generation job
        # For now, return True
        return True
