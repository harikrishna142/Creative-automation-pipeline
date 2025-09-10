"""
Asset Generator - Handles AI-powered image generation for products.
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from loguru import logger
from PIL import Image, ImageDraw, ImageFont
import requests
import httpx

try:
    from .models import Product, AspectRatio, CampaignBrief
    from .s3_storage import S3StorageManager
except ImportError:
    from models import Product, AspectRatio, CampaignBrief
    from s3_storage import S3StorageManager


class AssetGenerator:
    """
    Handles generation of product images using AI services.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the asset generator.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        #self.openai_api_key = config.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.dalle_model = config.get("dalle_model", "dall-e-3")
        self.gpt_model = config.get("gpt_model", "gpt-4.1")
        self.fallback_mode = config.get("fallback_mode", True)
        
        # Set up output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_api_key)
        except ImportError:
            logger.error("OpenAI library not installed")
            self.client = None
        
        # Initialize S3 storage
        self.s3_storage = S3StorageManager(config.get("s3_config", {}))
        
        # Mock product images for fallback
        self.mock_images = {
            "smartphone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800",
            "laptop": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800",
            "headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
            "watch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800",
            "camera": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800",
            "default": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800"
        }
    
    async def generate_product_image(
        self,
        campaign_brief: CampaignBrief,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        variation_num: int = 1
    ) -> Optional[Path]:
        """
        Generate a product image using AI or fallback methods.
        
        Args:
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory for the generated image
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            # Try AI generation first
            if self.openai_api_key:
                ai_image_path = await self._generate_with_dalle(campaign_brief, product, aspect_ratio, output_dir, variation_num)
                if ai_image_path:
                    return ai_image_path
            
            # Fallback to mock images
            if self.fallback_mode:
                return await self._generate_mock_image(product, aspect_ratio, output_dir)
            
            logger.warning(f"No AI API key available and fallback disabled for {product.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error generating image for {product.name}: {str(e)}")
            if self.fallback_mode:
                return await self._generate_mock_image(product, aspect_ratio, output_dir)
            return None
    
    async def _generate_with_dalle(
        self,
        campaign_brief: CampaignBrief,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        variation_num: int = 1
    ) -> Optional[Path]:
        """
        Generate image using DALL-E 3 or GPT-image-1 based on aspect ratio and avatar availability.
        
        Args:
            campaign_brief: Campaign brief with asset parameters
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory
            variation_num: Variation number for naming
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            # Check if we need to use GPT-image-1 for vertical aspect ratio with avatar
            if (aspect_ratio == AspectRatio.VERTICAL and 
                hasattr(campaign_brief, 'asset_params') and 
                campaign_brief.asset_params and 
                campaign_brief.asset_params.get('selected_avatar')):
                
                return await self._generate_with_gpt_image_1(campaign_brief, product, aspect_ratio, output_dir, variation_num)
            else:
                return await self._generate_with_dalle_3(campaign_brief, product, aspect_ratio, output_dir, variation_num)
                    
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    async def _generate_with_dalle_3(
        self,
        campaign_brief: CampaignBrief,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        variation_num: int = 1
    ) -> Optional[Path]:
        """
        Generate image using DALL-E 3 API.
        
        Args:
            campaign_brief: Campaign brief with asset parameters
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory
            variation_num: Variation number for naming
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            # Create prompt for DALL-E
            prompt = self._create_dalle_prompt(campaign_brief, product, aspect_ratio)
            size_mapping = {
                AspectRatio.SQUARE: "1024x1024",
                AspectRatio.VERTICAL: "1024x1792",
                AspectRatio.HORIZONTAL: "1792x1024"
            }
            size = size_mapping[aspect_ratio]
            
            # Call DALL-E 3 API
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "size": size,
                "quality": "standard",
                "n": 1
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    
                    # Download and save the image
                    image_path = await self._download_image(image_url, output_dir, aspect_ratio, variation_num)
                    logger.info(f"Successfully generated image with DALL-E 3 for {product.name}")
                    return image_path
                else:
                    logger.error(f"DALL-E 3 API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error with DALL-E 3 generation: {str(e)}")
            return None
    
    async def _generate_with_gpt_image_1(
        self,
        campaign_brief: CampaignBrief,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path,
        variation_num: int = 1
    ) -> Optional[Path]:
        """
        Generate image using GPT-image-1 with avatar input for vertical aspect ratio.
        
        Args:
            campaign_brief: Campaign brief with asset parameters
            product: Product information
            aspect_ratio: Target aspect ratio (should be VERTICAL)
            output_dir: Output directory
            variation_num: Variation number for naming
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            # Create prompt for GPT-image-1
            prompt = self._create_dalle_prompt(campaign_brief, product, aspect_ratio)
            
            # Get avatar image path
            avatar_path = campaign_brief.asset_params.get('selected_avatar')
            if not avatar_path or not Path(avatar_path).exists():
                logger.error(f"Avatar image not found: {avatar_path}")
                return None
            
            # Prepare the request for GPT-image-1 edits endpoint
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            # Prepare form data with image and prompt
            files = {
                'image': open(avatar_path, 'rb')
            }
            
            data = {
                'prompt': prompt,
                'model': 'gpt-image-1'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/edits",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle base64 response
                    if 'data' in result and len(result['data']) > 0:
                        image_data = result['data'][0]
                        
                        if 'b64_json' in image_data:
                            # Decode base64 image
                            import base64
                            image_bytes = base64.b64decode(image_data['b64_json'])
                            
                            # Save the image
                            image_path = await self._save_generated_image(
                                image_bytes, output_dir, aspect_ratio, variation_num
                            )
                            logger.info(f"Successfully generated image with GPT-image-1 for {product.name}")
                            return image_path
                        elif 'url' in image_data:
                            # Download from URL
                            image_path = await self._download_image(
                                image_data['url'], output_dir, aspect_ratio, variation_num
                            )
                            logger.info(f"Successfully generated image with GPT-image-1 for {product.name}")
                            return image_path
                    else:
                        logger.error(f"Unexpected GPT-image-1 response format: {result}")
                        return None
                else:
                    logger.error(f"GPT-image-1 API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error with GPT-image-1 generation: {str(e)}")
            return None
        finally:
            # Close the file if it was opened
            if 'files' in locals() and 'image' in files:
                files['image'].close()
    
    async def _generate_mock_image(
        self,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path
    ) -> Optional[Path]:
        """
        Generate a mock image using placeholder services or create a simple image.
        
        Args:
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory
            
        Returns:
            Path to generated image
        """
        try:
            # Try to find a relevant mock image
            image_url = None
            product_name_lower = product.name.lower()
            
            for keyword, url in self.mock_images.items():
                if keyword in product_name_lower:
                    image_url = url
                    break
            
            if not image_url:
                image_url = self.mock_images["default"]
            
            # Download the image
            image_path = await self._download_image(image_url, output_dir, aspect_ratio)
            
            if image_path:
                logger.info(f"Generated mock image for {product.name}")
                return image_path
            else:
                # Create a simple colored image as last resort
                return await self._create_simple_image(product, aspect_ratio, output_dir)
                
        except Exception as e:
            logger.error(f"Error generating mock image: {str(e)}")
            return await self._create_simple_image(product, aspect_ratio, output_dir)
    
    async def _download_image(self, image_url: str, output_dir: Path, aspect_ratio: AspectRatio, variation_num: int = 1) -> Optional[Path]:
        """
        Download image from URL and save to output directory.
        
        Args:
            image_url: URL of the image to download
            output_dir: Output directory
            aspect_ratio: Target aspect ratio
            
        Returns:
            Path to downloaded image or None if failed
        """
        try:
            image_id = str(uuid.uuid4())[:8]
            filename = f"variation{variation_num}_generated_{image_id}_{aspect_ratio.value.replace(':', 'x')}.jpg"
            image_path = output_dir / filename
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                
                if response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    
                    # Resize to target aspect ratio
                    await self._resize_to_aspect_ratio(image_path, aspect_ratio)
                    return image_path
                else:
                    logger.error(f"Failed to download image: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
    
    async def _save_generated_image(self, image_bytes: bytes, output_dir: Path, aspect_ratio: AspectRatio, variation_num: int = 1) -> Optional[Path]:
        """
        Save generated image bytes to output directory.
        
        Args:
            image_bytes: Image data as bytes
            output_dir: Output directory
            aspect_ratio: Target aspect ratio
            variation_num: Variation number for naming
            
        Returns:
            Path to saved image or None if failed
        """
        try:
            image_id = str(uuid.uuid4())[:8]
            filename = f"variation{variation_num}_generated_{image_id}_{aspect_ratio.value.replace(':', 'x')}.jpg"
            image_path = output_dir / filename
            
            # Save the image bytes
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            # Resize to target aspect ratio
            await self._resize_to_aspect_ratio(image_path, aspect_ratio)
            return image_path
                    
        except Exception as e:
            logger.error(f"Error saving generated image: {str(e)}")
            return None
    
    async def _create_simple_image(
        self,
        product: Product,
        aspect_ratio: AspectRatio,
        output_dir: Path
    ) -> Path:
        """
        Create a simple colored image with product name as fallback.
        
        Args:
            product: Product information
            aspect_ratio: Target aspect ratio
            output_dir: Output directory
            
        Returns:
            Path to created image
        """
        # Determine dimensions
        if aspect_ratio == AspectRatio.SQUARE:
            width, height = 1080, 1080
        elif aspect_ratio == AspectRatio.VERTICAL:
            width, height = 1080, 1920
        else:  # HORIZONTAL
            width, height = 1920, 1080
        
        # Create image with gradient background
        image = Image.new("RGB", (width, height), color=(70, 130, 180))
        draw = ImageDraw.Draw(image)
        
        # Add product name text
        try:
            # Try to use a system font
            font_size = min(width, height) // 20
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text = product.name
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with shadow
        draw.text((x + 2, y + 2), text, fill=(0, 0, 0), font=font)
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Save image
        image_id = str(uuid.uuid4())[:8]
        filename = f"simple_{image_id}_{aspect_ratio.value.replace(':', 'x')}.jpg"
        image_path = output_dir / filename
        image.save(image_path, "JPEG", quality=95)
        
        logger.info(f"Created simple image for {product.name}")
        return image_path
    
    async def _resize_to_aspect_ratio(self, image_path: Path, aspect_ratio: AspectRatio):
        """
        Resize image to target aspect ratio.
        
        Args:
            image_path: Path to image file
            aspect_ratio: Target aspect ratio
        """
        try:
            with Image.open(image_path) as img:
                # Calculate target dimensions
                if aspect_ratio == AspectRatio.SQUARE:
                    target_size = (1080, 1080)
                elif aspect_ratio == AspectRatio.VERTICAL:
                    target_size = (1080, 1920)
                else:  # HORIZONTAL
                    target_size = (1920, 1080)
                
                # Resize and crop to maintain aspect ratio
                img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                img_resized.save(image_path, "JPEG", quality=95)
                
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
    
    def _create_dalle_prompt(self, campaign_brief: CampaignBrief, product: Product, aspect_ratio: AspectRatio) -> str:
        """
        Create a prompt for DALL-E image generation.
        
        Args:
            product: Product information
            aspect_ratio: Target aspect ratio
            
        Returns:
            DALL-E prompt string
        """
        size_mapping = {
                AspectRatio.SQUARE: "1024x1024",
                AspectRatio.VERTICAL: "1024x1792",
                AspectRatio.HORIZONTAL: "1792x1024"
            }
        size = size_mapping[aspect_ratio]
        # --- Base product context ---
        base_prompt = f"generate social media ad marketing post image to promote {product.name} for a social advertising campaign for {campaign_brief.campaign_name}"
    
    # Product description
        if product.description:
            base_prompt += f" with a description: {product.description}"

        # Category
        if product.category:
            base_prompt += f" in the {product.category} category"

        # Features
        if product.features:
            features_text = ", ".join(product.features)
            base_prompt += f". Highlight key features: {features_text}"

        # Target demographic
        if product.target_demographic:
            base_prompt += f". Target audience: {product.target_demographic}"

        # --- Campaign context ---
        base_prompt += (
            f". Campaign: \"{campaign_brief.campaign_name}\" ({campaign_brief.campaign_id}) "
            f"for region {campaign_brief.target_region}, aimed at {campaign_brief.target_audience}."
        )

        if campaign_brief.campaign_message:
            base_prompt += f" Main campaign message: \"{campaign_brief.campaign_message}\"."
        
        # --- Asset parameters ---
        if hasattr(campaign_brief, 'asset_params') and campaign_brief.asset_params:
            asset_params = campaign_brief.asset_params
            
            # Add persona/avatar information only for 9:16 aspect ratio (vertical)
            if aspect_ratio.value == "9:16":
                # Check if a specific avatar was selected
                if asset_params.get('selected_avatar'):
                    avatar_path = asset_params.get('selected_avatar')
                    base_prompt += f" Use the person from the provided avatar image as the model wearing/using the {product.name}. The person should be the main focus of the image, demonstrating the product in use. Maintain the same person's appearance, facial features, and characteristics from the reference image."
                # Fallback to persona description
                elif asset_params.get('persona'):
                    persona = asset_params['persona']
                    base_prompt += f" Show a {persona.lower()} person wearing/using the {product.name}. The person should be the main focus of the image, demonstrating the product in use. Style should appeal to {persona.lower()}."
            
            # Add custom prompt context
            if asset_params.get('custom_prompt'):
                custom_prompt = asset_params['custom_prompt']
                base_prompt += f" Additional context: {custom_prompt}."
            
            # Add brand context
            if asset_params.get('brand'):
                brand = asset_params['brand']
                base_prompt += f" Brand: {brand}. Apply {brand} brand styling and guidelines."

        # --- Brand guidelines ---
        if campaign_brief.brand_guidelines:
            brand = campaign_brief.brand_guidelines
            base_prompt += (
                f" Follow brand guidelines: primary color {brand.get('primary_color')}, "
                f"secondary color {brand.get('secondary_color')}, "
                f"accent color {brand.get('accent_color')}, "
                f"font family {brand.get('font_family')}."
            )

        # --- Style descriptors ---
        style_prompt = (
            ", clean minimal background, professional studio lighting, "
            "high quality, modern commercial photography style"
        )

        # Add aspect ratio context
        if aspect_ratio == AspectRatio.VERTICAL:
            style_prompt += ", vertical composition suitable for mobile viewing, portrait orientation"
        elif aspect_ratio == AspectRatio.HORIZONTAL:
            style_prompt += ", horizontal composition suitable for desktop viewing, landscape orientation, product-focused"
        else:
            style_prompt += ", square composition suitable for social media, balanced layout"
        # --- Language ---
        if campaign_brief.language:
            style_prompt += f", text and style localized for {campaign_brief.language}"

        return base_prompt + style_prompt

    def generate_with_dalle(self, prompt: str, category: str = "general", asset_type: str = "image") -> str:
        """
        Generate an asset using DALL-E with proper categorization and processing.
        
        Args:
            prompt: The prompt for DALL-E generation
            category: Asset category (brand_logo, avatar, background, theme, etc.)
            asset_type: Type of asset (image, logo, avatar, etc.)
            
        Returns:
            Path to the generated and processed asset
        """
        try:
            # Check if OpenAI client is available
            if not self.client:
                raise Exception("OpenAI client not initialized. Please check your API key.")
            
            # Create category directory
            category_dir = self.output_dir / "assets" / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{category}_{asset_type}_{timestamp}.jpg"
            output_path = category_dir / filename
            
            # Call DALL-E API
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download and save image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            # Save original image
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            # Process and resize for different use cases
            self._process_asset_for_categories(output_path, category)
            
            # Upload to S3 if available
            if self.s3_storage.is_available():
                try:
                    # Use a generic campaign ID for asset generation
                    campaign_id = "asset_generation"
                    s3_url = asyncio.run(self.s3_storage.upload_asset(
                        local_file_path=output_path,
                        campaign_id=campaign_id,
                        asset_category=category
                    ))
                    if s3_url:
                        logger.info(f"Asset uploaded to S3: {s3_url}")
                except Exception as e:
                    logger.warning(f"Failed to upload asset to S3: {e}")
            
            logger.info(f"Generated {category} asset: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating {category} asset: {str(e)}")
            raise

    def _process_asset_for_categories(self, image_path: Path, category: str):
        """
        Process and resize assets based on their category for optimal use.
        
        Args:
            image_path: Path to the original image
            category: Asset category
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Choose one appropriate size based on category
                if category == "brand_logo":
                    # Logos work best at 512x512 for most use cases
                    target_size = (512, 512)
                    quality = 95
                
                elif category == "avatar":
                    # Avatars work best at 400x400 for profile pictures
                    target_size = (400, 400)
                    quality = 95
                
                elif category == "background":
                    # Backgrounds work best at 1920x1080 for most displays
                    target_size = (1920, 1080)
                    quality = 90
                
                elif category == "theme":
                    # Themes work best at 1024x1024 for versatility
                    target_size = (1024, 1024)
                    quality = 90
                
                else:  # general category
                    # General assets work best at 1024x1024
                    target_size = (1024, 1024)
                    quality = 90
                
                # Resize the image to the target size
                resized = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Save the processed image (overwrite the original)
                resized.save(image_path, "JPEG", quality=quality)
                
                # Save metadata
                metadata = {
                    "category": category,
                    "generated_at": datetime.now().isoformat(),
                    "original_size": img.size,
                    "processed_size": target_size,
                    "quality": quality
                }
                
                metadata_path = image_path.parent / f"{image_path.stem}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Processed {category} asset: {image_path} -> {target_size}")
                    
        except Exception as e:
            logger.error(f"Error processing asset {image_path}: {str(e)}")
            raise
