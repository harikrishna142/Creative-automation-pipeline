"""
Video generation component for creating short-form video advertisements.
Supports YouTube Shorts and Instagram Reels format (9:16 aspect ratio).
"""

import asyncio
import os
import random
from pathlib import Path
from typing import List, Optional, Dict, Any
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
# import moviepy.editor as mp
# from moviepy.video.fx import resize, crop
import requests
import json

try:
    from .models import Product, CampaignBrief, AspectRatio
    from .google_veo3_generator import GoogleVeo3Generator
except ImportError:
    from models import Product, CampaignBrief, AspectRatio
    from google_veo3_generator import GoogleVeo3Generator


class VideoGenerator:
    """Generates short-form video advertisements for social media platforms."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the video generator.
        
        Args:
            config: Configuration dictionary for video generation settings
        """
        self.config = config or {}
        self.output_dir = Path(self.config.get("output_dir", "output/videos"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Video settings
        self.video_duration = self.config.get("duration", 15)  # seconds
        self.fps = self.config.get("fps", 30)
        self.resolution = (1080, 1920)  # 9:16 aspect ratio for mobile
        self.background_music_volume = self.config.get("music_volume", 0.3)
        
        # Text overlay settings
        self.text_color = self.config.get("text_color", "#FFFFFF")
        self.text_outline_color = self.config.get("text_outline_color", "#000000")
        self.font_size = self.config.get("font_size", 60)
        
        # Available background music tracks (mock URLs - in production, use real music library)
        self.music_tracks = [
            "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",  # Mock URL
            "https://www.soundjay.com/misc/sounds/bell-ringing-06.wav",  # Mock URL
            "https://www.soundjay.com/misc/sounds/bell-ringing-07.wav",  # Mock URL
        ]
        
        # Mock voice generation (in production, use text-to-speech API)
        self.voice_enabled = self.config.get("voice_enabled", True)
        
        # Initialize Google Veo 3 generator
        self.veo3_generator = GoogleVeo3Generator(self.config.get("veo3_config", {}))
        self.use_veo3 = self.config.get("use_veo3", True)
        
    async def generate_video_ad(
        self,
        product: Product,
        campaign_brief: CampaignBrief,
        product_images: List[str],
        output_filename: str
    ) -> str:
        """Generate a short video advertisement.
        
        Args:
            product: Product information
            campaign_brief: Campaign brief with messaging
            product_images: List of product image paths
            output_filename: Output video filename
            
        Returns:
            Path to the generated video file
        """
        try:
            # Use Google Veo 3 if enabled and available
            if self.use_veo3:
                print("🎬 Generating video using Google Veo 3...")
                veo3_video = await self.veo3_generator.generate_video_ad(
                    product=product,
                    campaign_brief=campaign_brief,
                    product_images=product_images,
                    output_filename=output_filename
                )
                
                if veo3_video and Path(veo3_video).exists():
                    print(f"✅ Google Veo 3 video generated successfully: {veo3_video}")
                    return veo3_video
                else:
                    print("⚠️ Google Veo 3 generation failed, falling back to traditional method...")
            
            # Fallback to traditional video generation
            print("🎬 Generating video using traditional method...")
            video_path = await self._create_video_composition(
                product, campaign_brief, product_images, output_filename
            )
            
            # Add background music
            if self.config.get("add_music", True):
                video_path = await self._add_background_music(video_path)
            
            # Add voice-over
            if self.voice_enabled and campaign_brief.campaign_message:
                video_path = await self._add_voice_over(video_path, campaign_brief.campaign_message)
            
            return str(video_path)
            
        except Exception as e:
            print(f"Error generating video: {e}")
            # Return a mock video path for demo purposes
            return await self._create_mock_video(product, campaign_brief, output_filename)
    
    async def _create_video_composition(
        self,
        product: Product,
        campaign_brief: CampaignBrief,
        product_images: List[str],
        output_filename: str
    ) -> str:
        """Create the main video composition with images and text overlays."""
        
        # Create a list of clips
        clips = []
        
        # If we have product images, use them; otherwise create mock frames
        if product_images and all(Path(img).exists() for img in product_images):
            # Use actual product images
            for img_path in product_images:
                clip = mp.ImageClip(img_path, duration=self.video_duration / len(product_images))
                clip = clip.resize(height=self.resolution[1])
                clip = clip.crop(width=self.resolution[0], height=self.resolution[1], 
                               x_center=clip.w/2, y_center=clip.h/2)
                clips.append(clip)
        else:
            # Create mock frames with product information
            frames = await self._create_mock_frames(product, campaign_brief)
            for frame_path in frames:
                clip = mp.ImageClip(str(frame_path), duration=self.video_duration / len(frames))
                clips.append(clip)
        
        # Concatenate clips
        if clips:
            final_clip = mp.concatenate_videoclips(clips)
        else:
            # Fallback: create a simple text-based video
            final_clip = await self._create_text_video(product, campaign_brief)
        
        # Add text overlays
        final_clip = await self._add_text_overlays(final_clip, product, campaign_brief)
        
        # Export video
        output_path = self.output_dir / output_filename
        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()
        
        return str(output_path)
    
    async def _create_mock_frames(self, product: Product, campaign_brief: CampaignBrief) -> List[str]:
        """Create mock frames for demonstration purposes."""
        frames = []
        frame_duration = self.video_duration / 3  # 3 frames
        
        for i in range(3):
            # Create a frame with product information
            frame = Image.new('RGB', self.resolution, color='#1a1a1a')
            draw = ImageDraw.Draw(frame)
            
            # Try to use a system font
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
                title_font = ImageFont.truetype("arial.ttf", self.font_size + 20)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Add product name
            product_text = product.name
            bbox = draw.textbbox((0, 0), product_text, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.resolution[0] - text_width) // 2
            y = self.resolution[1] // 3
            
            # Draw text with outline
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), product_text, font=title_font, fill=self.text_outline_color)
            draw.text((x, y), product_text, font=title_font, fill=self.text_color)
            
            # Add campaign message
            if campaign_brief.campaign_message:
                message_text = campaign_brief.campaign_message
                bbox = draw.textbbox((0, 0), message_text, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.resolution[0] - text_width) // 2
                y = self.resolution[1] // 2
                
                # Draw message with outline
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), message_text, font=font, fill=self.text_outline_color)
                draw.text((x, y), message_text, font=font, fill=self.text_color)
            
            # Add price if available
            if product.price:
                price_text = f"${product.price:.2f}"
                bbox = draw.textbbox((0, 0), price_text, font=font)
                text_width = bbox[2] - bbox[0]
                x = (self.resolution[0] - text_width) // 2
                y = self.resolution[1] * 2 // 3
                
                # Draw price with outline
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), price_text, font=font, fill=self.text_outline_color)
                draw.text((x, y), price_text, font=font, fill="#FFD700")  # Gold color for price
            
            # Save frame
            frame_path = self.output_dir / f"frame_{i}.png"
            frame.save(frame_path)
            frames.append(str(frame_path))
        
        return frames
    
    async def _create_text_video(self, product: Product, campaign_brief: CampaignBrief) -> mp.VideoClip:
        """Create a simple text-based video as fallback."""
        # Create a simple colored background
        def make_frame(t):
            # Create a gradient background
            frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
            # Simple gradient from dark to light
            gradient = int(255 * (t / self.video_duration))
            frame[:, :] = [gradient // 3, gradient // 2, gradient]
            return frame
        
        clip = mp.VideoClip(make_frame, duration=self.video_duration)
        return clip
    
    async def _add_text_overlays(
        self, 
        clip: mp.VideoClip, 
        product: Product, 
        campaign_brief: CampaignBrief
    ) -> mp.VideoClip:
        """Add text overlays to the video."""
        
        # Product name overlay
        product_text = mp.TextClip(
            product.name,
            fontsize=self.font_size,
            color=self.text_color,
            stroke_color=self.text_outline_color,
            stroke_width=2
        ).set_position(('center', 0.2), relative=True).set_duration(self.video_duration)
        
        # Campaign message overlay
        message_text = mp.TextClip(
            campaign_brief.campaign_message,
            fontsize=self.font_size - 10,
            color=self.text_color,
            stroke_color=self.text_outline_color,
            stroke_width=1
        ).set_position(('center', 0.5), relative=True).set_duration(self.video_duration)
        
        # Price overlay (if available)
        if product.price:
            price_text = mp.TextClip(
                f"${product.price:.2f}",
                fontsize=self.font_size - 5,
                color="#FFD700",
                stroke_color=self.text_outline_color,
                stroke_width=2
            ).set_position(('center', 0.8), relative=True).set_duration(self.video_duration)
            
            # Composite all text overlays
            final_clip = mp.CompositeVideoClip([clip, product_text, message_text, price_text])
        else:
            # Composite without price
            final_clip = mp.CompositeVideoClip([clip, product_text, message_text])
        
        return final_clip
    
    async def _add_background_music(self, video_path: str) -> str:
        """Add background music to the video."""
        try:
            # Load the video
            video = mp.VideoFileClip(video_path)
            
            # Select a random music track (in production, use proper music library)
            music_url = random.choice(self.music_tracks)
            
            # For demo purposes, create a simple audio track
            # In production, download and use actual music
            audio_clip = mp.AudioClip(lambda t: np.sin(440 * 2 * np.pi * t) * 0.1, duration=self.video_duration)
            
            # Set the volume
            audio_clip = audio_clip.volumex(self.background_music_volume)
            
            # Add audio to video
            final_video = video.set_audio(audio_clip)
            
            # Export with audio
            output_path = video_path.replace('.mp4', '_with_music.mp4')
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video.close()
            audio_clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error adding background music: {e}")
            return video_path  # Return original if music addition fails
    
    async def _add_voice_over(self, video_path: str, message: str) -> str:
        """Add voice-over to the video."""
        try:
            # Load the video
            video = mp.VideoFileClip(video_path)
            
            # In production, use text-to-speech API (e.g., Google TTS, Azure Speech, etc.)
            # For demo purposes, create a simple beep sound
            voice_clip = mp.AudioClip(lambda t: np.sin(880 * 2 * np.pi * t) * 0.2, duration=min(5, self.video_duration))
            
            # Mix with existing audio if present
            if video.audio:
                final_audio = mp.CompositeAudioClip([video.audio, voice_clip])
            else:
                final_audio = voice_clip
            
            # Set the final audio
            final_video = video.set_audio(final_audio)
            
            # Export with voice-over
            output_path = video_path.replace('.mp4', '_with_voice.mp4')
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video.close()
            voice_clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error adding voice-over: {e}")
            return video_path  # Return original if voice-over addition fails
    
    async def _create_mock_video(self, product: Product, campaign_brief: CampaignBrief, output_filename: str) -> str:
        """Create a mock video for demonstration purposes when real generation fails."""
        try:
            # Create a simple animated video
            def make_frame(t):
                # Create a frame with product information
                frame = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
                
                # Animate background color
                color_intensity = int(128 + 127 * np.sin(t * 2 * np.pi / self.video_duration))
                frame[:, :] = [color_intensity // 3, color_intensity // 2, color_intensity]
                
                return frame
            
            # Create video clip
            clip = mp.VideoClip(make_frame, duration=self.video_duration)
            
            # Add text overlays
            clip = await self._add_text_overlays(clip, product, campaign_brief)
            
            # Export
            output_path = self.output_dir / output_filename
            clip.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            clip.close()
            return str(output_path)
            
        except Exception as e:
            print(f"Error creating mock video: {e}")
            # Return a placeholder path
            return str(self.output_dir / output_filename)
