"""
Creative Automation Pipeline - Main pipeline class for generating social media campaign assets.
"""

import os
import json
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from loguru import logger
from PIL import Image, ImageDraw, ImageFont
import requests

try:
    from .models import (
        CampaignBrief, GeneratedCreative, GeneratedVideo, CampaignOutput, 
        GenerationRequest, AspectRatio, AssetInfo, ContentType, VideoFormat
    )
    from .asset_generator import AssetGenerator
    from .template_engine import TemplateEngine
    from .quality_checker import QualityChecker
    from .video_generator_simple import VideoGenerator
    from .s3_storage import S3StorageManager
except ImportError:
    # For standalone execution
    from models import (
        CampaignBrief, GeneratedCreative, GeneratedVideo, CampaignOutput, 
        GenerationRequest, AspectRatio, AssetInfo, ContentType, VideoFormat
    )
    from asset_generator import AssetGenerator
    from template_engine import TemplateEngine
    from quality_checker import QualityChecker
    from video_generator_simple import VideoGenerator
    from s3_storage import S3StorageManager


class CreativePipeline:
    """
    Main creative automation pipeline that orchestrates the generation of social media campaign assets.
    """
    
    def __init__(self, output_dir: str = "output", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the creative pipeline.
        
        Args:
            output_dir: Directory to save generated assets
            config: Configuration dictionary for the pipeline
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.config = config or {}
        self.asset_generator = AssetGenerator(config.get("ai_config", {}))
        self.template_engine = TemplateEngine(config.get("template_config", {}))
        self.quality_checker = QualityChecker(config.get("quality_config", {}))
        self.video_generator = VideoGenerator(config.get("video_config", {}))
        self.s3_storage = S3StorageManager(config.get("s3_config", {}))
        
        # Create subdirectories
        self.assets_dir = self.output_dir / "assets"
        self.templates_dir = self.output_dir / "templates"
        self.videos_dir = self.output_dir / "videos"
        self.logs_dir = self.output_dir / "logs"
        
        for dir_path in [self.assets_dir, self.templates_dir, self.videos_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        logger.add(
            self.logs_dir / "pipeline.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    async def process_campaign(self, request: GenerationRequest) -> CampaignOutput:
        """
        Process a complete campaign and generate all required creatives.
        
        Args:
            request: Generation request containing campaign brief and parameters
            
        Returns:
            CampaignOutput with all generated creatives and metadata
        """
        campaign_brief = request.campaign_brief
        campaign_id = campaign_brief.campaign_id
        
        logger.info(f"Starting campaign processing for {campaign_id}")
        
        # Create campaign-specific output directory
        campaign_dir = self.output_dir / campaign_id
        campaign_dir.mkdir(exist_ok=True)
        
        generated_creatives = []
        generated_videos = []
        generation_errors = []
        
        # Process each product
        for product in campaign_brief.products:
            logger.info(f"Processing product: {product.name}")
            
            # Create product-specific directory
            product_dir = campaign_dir / product.name.replace(" ", "_").lower()
            product_dir.mkdir(exist_ok=True)
            
            # Generate creatives (only if not video-only)
            if campaign_brief.content_type in [ContentType.IMAGE, ContentType.BOTH]:
                # Generate 3 variations for each product
                num_variations = 3
                variation_num = 1
                for aspect_ratio in campaign_brief.aspect_ratios:
                    logger.info(f"Generating variation {variation_num} for {product.name}")
                    
                    try:
                        # Generate base image for this variation
                        base_image_path = await self._get_or_generate_base_image(
                            product=product,
                            aspect_ratio=aspect_ratio,
                            campaign_brief=campaign_brief,
                            variation_num=variation_num
                        )
                        
                        if base_image_path and base_image_path.exists():
                            # Create aspect ratio folders and generate all ratios for this variation
                            
                            try:
                                creative = await self._generate_single_creative(
                                    campaign_brief=campaign_brief,
                                    product=product,
                                    aspect_ratio=aspect_ratio,
                                    output_dir=product_dir,
                                    input_assets=request.input_assets,
                                    base_image_path=base_image_path,
                                    variation_num=variation_num
                                )
                                    
                                if creative:
                                    generated_creatives.append(creative)
                                    logger.info(f"Generated creative for {product.name} - Variation {variation_num} - {aspect_ratio}")
                                else:
                                    generation_errors.append(f"Failed to generate creative for {product.name} - Variation {variation_num} - {aspect_ratio}")
                                        
                            except Exception as e:
                                error_msg = f"Error generating creative for {product.name} - Variation {variation_num} - {aspect_ratio}: {str(e)}"
                                logger.error(error_msg)
                                generation_errors.append(error_msg)
                        else:
                            generation_errors.append(f"Failed to generate base image for {product.name} - Variation {variation_num}")
                            
                    except Exception as e:
                        error_msg = f"Error generating variation {variation_num} for {product.name}: {str(e)}"
                        logger.error(error_msg)
                        generation_errors.append(error_msg)
                    variation_num += 1
            else:
                logger.info(f"Skipping image generation for {product.name} - Video Only mode")
        
        # Generate videos if requested
        if campaign_brief.content_type in [ContentType.VIDEO, ContentType.BOTH]:
            logger.info("Starting video generation...")
            
            for product in campaign_brief.products:
                try:
                    # Get product images for video generation
                    product_images = []
                    for creative in generated_creatives:
                        if creative.product_name == product.name:
                            product_images.append(creative.file_path)
                    
                    # Generate video for each requested format
                    video_formats = [campaign_brief.video_format] if campaign_brief.video_format else [
                        VideoFormat.YOUTUBE_SHORTS, VideoFormat.INSTAGRAM_REELS
                    ]
                    
                    for video_format in video_formats:
                        # Create cleaner video filename
                        product_name_clean = product.name.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()
                        video_format_clean = video_format.value.replace(" ", "_").lower()
                        video_filename = f"{product_name_clean}_{video_format_clean}_{int(time.time())}.mp4"
                        
                        # Track generation time
                        start_time = time.time()
                        video_path = await self.video_generator.generate_video_ad(
                            product=product,
                            campaign_brief=campaign_brief,
                            product_images=product_images,
                            output_filename=video_filename
                        )
                        generation_time_seconds = time.time() - start_time
                        
                        if video_path and Path(video_path).exists():
                            # Create GeneratedVideo object
                            video = GeneratedVideo(
                                video_id=str(uuid.uuid4()),
                                product_name=product.name,
                                video_format=video_format,
                                file_path=video_path,
                                duration=campaign_brief.video_duration,
                                resolution={"width": 1080, "height": 1920},
                                fps=30,
                                has_music=campaign_brief.include_music,
                                has_voice_over=campaign_brief.include_voice_over,
                                quality_score=0.8,  # Mock quality score
                                generation_time=generation_time_seconds,
                                ai_model_used="video_generator"
                            )
                            generated_videos.append(video)
                            logger.info(f"Generated video for {product.name} - {video_format}")
                        else:
                            generation_errors.append(f"Failed to generate video for {product.name} - {video_format}")
                            
                except Exception as e:
                    error_msg = f"Error generating video for {product.name}: {str(e)}"
                    logger.error(error_msg)
                    generation_errors.append(error_msg)
        
        # Calculate success metrics
        total_expected = len(campaign_brief.products) * len(campaign_brief.aspect_ratios)
        success_rate = len(generated_creatives) / total_expected if total_expected > 0 else 0
        
        # Create generation summary
        generation_summary = {
            "total_expected": total_expected,
            "total_generated": len(generated_creatives),
            "success_rate": success_rate,
            "errors": generation_errors,
            "generation_time": datetime.now().isoformat(),
            "campaign_id": campaign_id
        }
        
        # Save summary to file
        summary_file = campaign_dir / "generation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(generation_summary, f, indent=2)
        
        logger.info(f"Campaign processing completed. Success rate: {success_rate:.2%}")
        
        # Create campaign output
        campaign_output = CampaignOutput(
            campaign_id=campaign_id,
            campaign_name=campaign_brief.campaign_name,
            generated_creatives=generated_creatives,
            generated_videos=generated_videos,
            generation_summary=generation_summary,
            output_directory=str(campaign_dir),
            total_creatives=len(generated_creatives),
            total_videos=len(generated_videos),
            success_rate=success_rate
        )
        
        # Store campaign data in S3 if available
        if self.s3_storage.is_available():
            try:
                # Store campaign brief
                campaign_brief_url = await self.s3_storage.store_campaign_brief(campaign_brief, campaign_id)
                if campaign_brief_url:
                    logger.info(f"Campaign brief stored in S3: {campaign_brief_url}")
                
                # Store campaign output
                campaign_output_url = await self.s3_storage.store_campaign_output(campaign_output, campaign_id)
                if campaign_output_url:
                    logger.info(f"Campaign output stored in S3: {campaign_output_url}")
                
                # Upload generated creatives to S3
                for creative in generated_creatives:
                    if creative.file_path and Path(creative.file_path).exists():
                        s3_url = await self.s3_storage.upload_creative(
                            local_file_path=creative.file_path,
                            campaign_id=campaign_id,
                            product_name=creative.product_name,
                            aspect_ratio=creative.aspect_ratio,
                            variation_num=creative.variation_num
                        )
                        if s3_url:
                            creative.s3_url = s3_url
                            logger.info(f"Creative uploaded to S3: {s3_url}")
                
                # Upload generated videos to S3
                for video in generated_videos:
                    if video.file_path and Path(video.file_path).exists():
                        s3_url = await self.s3_storage.upload_video(
                            local_file_path=video.file_path,
                            campaign_id=campaign_id,
                            product_name=video.product_name,
                            video_format=video.video_format
                        )
                        if s3_url:
                            video.s3_url = s3_url
                            logger.info(f"Video uploaded to S3: {s3_url}")
                            
            except Exception as e:
                logger.error(f"Error storing campaign data in S3: {e}")
        else:
            logger.info("S3 storage not available. Campaign data stored locally only.")
        
        return campaign_output
    
    async def _generate_single_creative(
        self,
        campaign_brief: CampaignBrief,
        product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        input_assets: List[AssetInfo],
        base_image_path: Path = None,
        variation_num: int = 1
    ) -> Optional[GeneratedCreative]:
        """
        Generate a single creative for a specific product and aspect ratio.
        
        Args:
            campaign_brief: Campaign brief information
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory for the creative
            input_assets: Available input assets
            base_image_path: Pre-generated base image path
            variation_num: Variation number (1, 2, 3)
            
        Returns:
            GeneratedCreative object or None if generation failed
        """
        creative_id = str(uuid.uuid4())
        
        # Create aspect ratio folder
        aspect_ratio_folder = output_dir / aspect_ratio.value.replace(':', 'x')
        aspect_ratio_folder.mkdir(exist_ok=True)
        
        if not base_image_path or not base_image_path.exists():
            logger.error(f"Base image not provided or doesn't exist for {product.name} variation {variation_num}")
            return None
        
        # Apply template and add text
        final_creative_path = await self._apply_template_and_text(
            base_image_path=base_image_path,
            campaign_brief=campaign_brief,
            product=product,
            aspect_ratio=aspect_ratio,
            output_dir=aspect_ratio_folder,
            creative_id=creative_id,
            variation_num=variation_num
        )
        
        if not final_creative_path:
            logger.error(f"Failed to apply template for {product.name}")
            return None
        
        # Quality check
        quality_score = await self.quality_checker.check_creative_quality(
            image_path=final_creative_path,
            campaign_brief=campaign_brief,
            product=product
        )
        
        # Create metadata
        generation_metadata = {
            "base_image_path": str(base_image_path),
            "template_applied": True,
            "quality_score": quality_score,
            "generation_time": datetime.now().isoformat(),
            "aspect_ratio": aspect_ratio.value,
            "product_name": product.name
        }
        
        return GeneratedCreative(
            creative_id=creative_id,
            product_name=product.name,
            aspect_ratio=aspect_ratio,
            file_path=str(final_creative_path),
            campaign_message=campaign_brief.campaign_message,
            generation_metadata=generation_metadata,
            quality_score=quality_score,
            variation_num=variation_num
        )
    
    async def _get_or_generate_base_image(
        self,
        campaign_brief: CampaignBrief,
        product,
        aspect_ratio: AspectRatio,
        variation_num: int = 1,
        existing_assets: List[AssetInfo] = None
    ) -> Optional[Path]:
        """
        Get existing base image or generate a new one using AI.
        
        Args:
            campaign_brief: Campaign brief information
            product: Product information
            variation_num: Variation number (1, 2, 3)
            existing_assets: Available input assets
            
        Returns:
            Path to base image or None if failed
        """
        # For now, always generate new variations using AI
        # In the future, we could check for existing assets and create variations from them
        
        # Generate new image variation using AI
        logger.info(f"Generating variation {variation_num} for {product.name} using AI")
        
        # Create a temporary directory for base images
        base_images_dir = Path("output/temp_base_images")
        base_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate base image for this variation
        generated_path = await self.asset_generator.generate_product_image(
            campaign_brief, 
            product, 
            aspect_ratio,  # Generate as square first, then resize to other ratios
            base_images_dir,
            variation_num=variation_num
        )
        
        return generated_path
    
    async def _apply_template_and_text(
        self,
        base_image_path: Path,
        campaign_brief: CampaignBrief,
        product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        creative_id: str,
        variation_num: int = 1
    ) -> Optional[Path]:
        """
        Apply template and add campaign text to the base image.
        
        Args:
            base_image_path: Path to base image
            campaign_brief: Campaign brief
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory
            creative_id: Creative identifier
            
        Returns:
            Path to final creative or None if failed
        """
        try:
            # Create a cleaner filename with product name, variation number, and aspect ratio
            product_name_clean = product.name.replace(" ", "_").replace("/", "_").replace("\\", "_").lower()
            aspect_ratio_clean = aspect_ratio.value.replace(':', 'x')
            final_path = output_dir / f"variation{variation_num}_{product_name_clean}_{aspect_ratio_clean}_{creative_id[:8]}.jpg"
            
            # Apply template using template engine
            await self.template_engine.apply_template(
                base_image_path=base_image_path,
                campaign_brief=campaign_brief,
                product=product,
                aspect_ratio=aspect_ratio,
                output_path=final_path
            )
            
            return final_path
            
        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
            return None
    
    async def _resize_image(self, input_path: Path, output_path: Path, aspect_ratio: AspectRatio):
        """
        Resize image to target aspect ratio.
        
        Args:
            input_path: Input image path
            output_path: Output image path
            aspect_ratio: Target aspect ratio
        """
        try:
            with Image.open(input_path) as img:
                # Calculate target dimensions
                if aspect_ratio == AspectRatio.SQUARE:
                    target_size = (1080, 1080)
                elif aspect_ratio == AspectRatio.VERTICAL:
                    target_size = (1080, 1920)
                else:  # HORIZONTAL
                    target_size = (1920, 1080)
                
                # Resize and crop to maintain aspect ratio
                img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                img_resized.save(output_path, "JPEG", quality=95)
                
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            raise
