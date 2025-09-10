"""
Template Engine - Handles applying templates and adding text to generated images.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import uuid

from loguru import logger
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import httpx
import os


class TemplateEngine:
    """
    Handles applying templates and adding campaign text to images.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the template engine.
        
        Args:
            config: Configuration dictionary for template settings
        """
        self.config = config
        self.default_font_size = config.get("default_font_size", 48)
        self.text_color = config.get("text_color", (255, 255, 255))
        
        # Brand templates
        self.brand_templates = {
            "Nike": {
                "primary_color": (0, 0, 0),  # Black
                "secondary_color": (255, 255, 255),  # White
                "accent_color": (255, 0, 0),  # Red
                "font_style": "bold",
                "logo_position": "bottom_right",
                "brand_guidelines": "Just Do It - Bold, athletic, motivational"
            },
            "Adidas": {
                "primary_color": (0, 0, 0),  # Black
                "secondary_color": (255, 255, 255),  # White
                "accent_color": (0, 150, 0),  # Green
                "font_style": "bold",
                "logo_position": "bottom_left",
                "brand_guidelines": "Impossible is Nothing - Sporty, innovative, three stripes"
            },
            "Coca-Cola": {
                "primary_color": (255, 0, 0),  # Red
                "secondary_color": (255, 255, 255),  # White
                "accent_color": (0, 0, 0),  # Black
                "font_style": "script",
                "logo_position": "top_center",
                "brand_guidelines": "Taste the Feeling - Classic, refreshing, happiness"
            },
            "Apple": {
                "primary_color": (0, 0, 0),  # Black
                "secondary_color": (255, 255, 255),  # White
                "accent_color": (100, 100, 100),  # Gray
                "font_style": "minimal",
                "logo_position": "top_left",
                "brand_guidelines": "Think Different - Clean, minimalist, premium"
            },
            "Samsung": {
                "primary_color": (0, 0, 139),  # Blue
                "secondary_color": (255, 255, 255),  # White
                "accent_color": (255, 165, 0),  # Orange
                "font_style": "modern",
                "logo_position": "bottom_center",
                "brand_guidelines": "Innovation for Everyone - Technology, innovation, accessible"
            }
        }
        self.text_outline_color = config.get("text_outline_color", (0, 0, 0))
        self.text_position = config.get("text_position", "bottom")
        self.brand_colors = config.get("brand_colors", {
            "primary": (70, 130, 180),
            "secondary": (255, 255, 255),
            "accent": (255, 215, 0)
        })
    
    async def apply_template(
        self,
        base_image_path: Path,
        campaign_brief,
        product,
        aspect_ratio,
        output_path: Path
    ) -> bool:
        """
        Apply template and add campaign text to the base image.
        
        Args:
            base_image_path: Path to the base image
            campaign_brief: Campaign brief information
            product: Product information
            aspect_ratio: Target aspect ratio
            output_path: Path to save the final creative
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load the base image
            with Image.open(base_image_path) as base_image:
                # Create a copy to work with
                creative_image = base_image.copy()
                
                # Apply image enhancements
                creative_image = await self._enhance_image(creative_image)
                
                # Add overlay elements
                creative_image = await self._add_overlay_elements(
                    creative_image, aspect_ratio, product
                )
                
                # Add campaign text
                creative_image = await self._add_campaign_text(
                    creative_image, campaign_brief, product, aspect_ratio
                )
                
                # Add brand elements
                creative_image = await self._add_brand_elements(
                    creative_image, aspect_ratio, campaign_brief
                )
                
                # Save the final creative
                creative_image.save(output_path, "JPEG", quality=95)
                
                logger.info(f"Successfully applied template to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
            return False
    
    async def _enhance_image(self, image: Image.Image) -> Image.Image:
        """
        Apply image enhancements like contrast, brightness, and sharpness.
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        try:
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.05)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            logger.error(f"Error enhancing image: {str(e)}")
            return image
    
    async def _add_overlay_elements(
        self,
        image: Image.Image,
        aspect_ratio,
        product
    ) -> Image.Image:
        """
        Add overlay elements like gradients, shapes, or decorative elements.
        
        Args:
            image: Input image
            aspect_ratio: Target aspect ratio
            product: Product information
            
        Returns:
            Image with overlay elements
        """
        try:
            width, height = image.size
            draw = ImageDraw.Draw(image)
            
            # Add a subtle gradient overlay at the bottom for text readability
            if aspect_ratio.value == "9:16":  # Vertical
                overlay_height = height // 3
                overlay_y = height - overlay_height
                
                # Create gradient overlay
                for i in range(overlay_height):
                    alpha = int(100 * (1 - i / overlay_height))
                    color = (*self.brand_colors["primary"], alpha)
                    
                    # Draw semi-transparent rectangle
                    overlay = Image.new("RGBA", (width, 1), color)
                    image.paste(overlay, (0, overlay_y + i), overlay)
            
            # Add a subtle border
            border_width = 4
            border_color = self.brand_colors["accent"]
            draw.rectangle(
                [0, 0, width - 1, height - 1],
                outline=border_color,
                width=border_width
            )
            
            return image
            
        except Exception as e:
            logger.error(f"Error adding overlay elements: {str(e)}")
            return image
    
    async def _add_campaign_text(
        self,
        image: Image.Image,
        campaign_brief,
        product,
        aspect_ratio
    ) -> Image.Image:
        """
        Add campaign text to the image.
        
        Args:
            image: Input image
            campaign_brief: Campaign brief information
            product: Product information
            aspect_ratio: Target aspect ratio
            
        Returns:
            Image with campaign text
        """
        try:
            width, height = image.size
            draw = ImageDraw.Draw(image)
            
            # Calculate font size based on image dimensions
            base_font_size = min(width, height) // 25
            title_font_size = int(base_font_size * 1.2)
            subtitle_font_size = int(base_font_size * 0.8)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("arial.ttf", title_font_size)
                subtitle_font = ImageFont.truetype("arial.ttf", subtitle_font_size)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Prepare text content
            campaign_message = campaign_brief.campaign_message
            product_name = product.name
            
            # Apply brand template if specified
            brand_template = None
            if hasattr(campaign_brief, 'asset_params') and campaign_brief.asset_params:
                brand_name = campaign_brief.asset_params.get('brand')
                if brand_name and brand_name in self.brand_templates:
                    brand_template = self.brand_templates[brand_name]
                    logger.info(f"Applying {brand_name} brand template")
            
            # Translate campaign message if language is not English
            if campaign_brief.language and campaign_brief.language != "en":
                campaign_message = await self._translate_text_with_openai(
                    campaign_message, campaign_brief.language
                )
            
            # Calculate text positions
            if aspect_ratio.value == "9:16":  # Vertical
                # Position text at the bottom
                text_y_start = height - (height // 4)
                text_x = width // 2
                
                # Draw product name
                product_bbox = draw.textbbox((0, 0), product_name, font=title_font)
                product_width = product_bbox[2] - product_bbox[0]
                product_x = (width - product_width) // 2
                
                # Apply brand colors if template is available
                text_color = self.text_color
                outline_color = self.text_outline_color
                if brand_template:
                    text_color = brand_template["secondary_color"]
                    outline_color = brand_template["primary_color"]
                
                # Draw with outline
                self._draw_text_with_outline(
                    draw, product_name, (product_x, text_y_start),
                    title_font, text_color, outline_color
                )
                
                # Draw campaign message
                message_bbox = draw.textbbox((0, 0), campaign_message, font=subtitle_font)
                message_width = message_bbox[2] - message_bbox[0]
                message_x = (width - message_width) // 2
                message_y = text_y_start + title_font_size + 20
                
                self._draw_text_with_outline(
                    draw, campaign_message, (message_x, message_y),
                    subtitle_font, text_color, outline_color
                )
                
            else:  # Square or horizontal
                # Position text at the bottom
                text_y_start = height - (height // 5)
                text_x = width // 2
                
                # Draw product name
                product_bbox = draw.textbbox((0, 0), product_name, font=title_font)
                product_width = product_bbox[2] - product_bbox[0]
                product_x = (width - product_width) // 2
                
                # Apply brand colors if template is available
                text_color = self.text_color
                outline_color = self.text_outline_color
                if brand_template:
                    text_color = brand_template["secondary_color"]
                    outline_color = brand_template["primary_color"]
                
                self._draw_text_with_outline(
                    draw, product_name, (product_x, text_y_start),
                    title_font, text_color, outline_color
                )
                
                # Draw campaign message
                message_bbox = draw.textbbox((0, 0), campaign_message, font=subtitle_font)
                message_width = message_bbox[2] - message_bbox[0]
                message_x = (width - message_width) // 2
                message_y = text_y_start + title_font_size + 15
                
                self._draw_text_with_outline(
                    draw, campaign_message, (message_x, message_y),
                    subtitle_font, text_color, outline_color
                )
            
            return image
            
        except Exception as e:
            logger.error(f"Error adding campaign text: {str(e)}")
            return image
    
    async def _add_brand_elements(
        self,
        image: Image.Image,
        aspect_ratio,
        campaign_brief=None
    ) -> Image.Image:
        """
        Add brand elements like logos or brand colors.
        
        Args:
            image: Input image
            aspect_ratio: Target aspect ratio
            campaign_brief: Campaign brief with asset parameters
            
        Returns:
            Image with brand elements
        """
        try:
            width, height = image.size
            draw = ImageDraw.Draw(image)
            
            # Check if we should add a brand logo
            brand_logo_path = None
            if campaign_brief and hasattr(campaign_brief, 'asset_params') and campaign_brief.asset_params:
                asset_params = campaign_brief.asset_params
                
                # Check if a specific brand logo was selected
                if asset_params.get('selected_brand_logo'):
                    brand_logo_path = Path(asset_params.get('selected_brand_logo'))
                # Fallback to finding brand logo by brand name
                elif asset_params.get('use_brand_logo', False):
                    brand_logo_path = self._find_brand_logo(asset_params.get('brand'))
            
            if brand_logo_path and brand_logo_path.exists():
                # Add brand logo
                await self._add_brand_logo(image, brand_logo_path, aspect_ratio)
            else:
                # Fallback to simple brand indicator
                await self._add_simple_brand_indicator(image, draw, width, height)
            
            return image
            
        except Exception as e:
            logger.error(f"Error adding brand elements: {str(e)}")
            return image

    def _find_brand_logo(self, brand_name: str) -> Optional[Path]:
        """
        Find brand logo in the assets directory.
        
        Args:
            brand_name: Name of the brand
            
        Returns:
            Path to brand logo if found, None otherwise
        """
        if not brand_name:
            return None
            
        try:
            # Look in brand_logo category directory
            assets_dir = Path("output/assets/brand_logo")
            if not assets_dir.exists():
                return None
            
            # Look for files that might contain the brand name
            brand_name_lower = brand_name.lower()
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.svg"]:
                for logo_file in assets_dir.glob(ext):
                    if brand_name_lower in logo_file.name.lower():
                        return logo_file
            
            # If no specific brand logo found, look for any logo
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.svg"]:
                logos = list(assets_dir.glob(ext))
                if logos:
                    return logos[0]  # Return first available logo
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding brand logo: {str(e)}")
            return None

    async def _add_brand_logo(self, image: Image.Image, logo_path: Path, aspect_ratio) -> None:
        """
        Add brand logo to the image.
        
        Args:
            image: Input image
            logo_path: Path to the logo file
            aspect_ratio: Target aspect ratio
        """
        try:
            width, height = image.size
            
            # Load logo
            logo = Image.open(logo_path)
            
            # Convert to RGBA if needed
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Calculate logo size based on image dimensions
            logo_size = min(width, height) // 8  # Logo should be 1/8 of the smaller dimension
            
            # Resize logo while maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Determine logo position based on aspect ratio and brand template
            logo_x, logo_y = self._get_logo_position(width, height, logo.size, aspect_ratio)
            
            # Create a white background for the logo if it's transparent
            if logo.mode == 'RGBA':
                # Create a white background
                logo_bg = Image.new('RGB', logo.size, (255, 255, 255))
                logo_bg.paste(logo, mask=logo.split()[-1])  # Use alpha channel as mask
                logo = logo_bg
            
            # Paste logo onto image
            image.paste(logo, (logo_x, logo_y))
            
            logger.info(f"Added brand logo from {logo_path} at position ({logo_x}, {logo_y})")
            
        except Exception as e:
            logger.error(f"Error adding brand logo: {str(e)}")

    def _get_logo_position(self, image_width: int, image_height: int, logo_size: tuple, aspect_ratio) -> tuple:
        """
        Get logo position based on aspect ratio and brand guidelines.
        
        Args:
            image_width: Width of the main image
            image_height: Height of the main image
            logo_size: Size of the logo (width, height)
            aspect_ratio: Target aspect ratio
            
        Returns:
            Tuple of (x, y) position for the logo
        """
        logo_w, logo_h = logo_size
        
        # Default position (bottom right with margin)
        margin = 20
        x = image_width - logo_w - margin
        y = image_height - logo_h - margin
        
        # Adjust position based on aspect ratio
        if aspect_ratio.value == "9:16":  # Vertical
            # For vertical images, place logo at bottom center
            x = (image_width - logo_w) // 2
            y = image_height - logo_h - margin
        elif aspect_ratio.value == "16:9":  # Horizontal
            # For horizontal images, place logo at top right
            x = image_width - logo_w - margin
            y = margin
        else:  # Square
            # For square images, place logo at bottom right
            x = image_width - logo_w - margin
            y = image_height - logo_h - margin
        
        return (x, y)

    async def _add_simple_brand_indicator(self, image: Image.Image, draw: ImageDraw.Draw, width: int, height: int) -> None:
        """
        Add a simple brand indicator (fallback when no logo is available).
        
        Args:
            image: Input image
            draw: ImageDraw object
            width: Image width
            height: Image height
        """
        try:
            # Add a small brand indicator (simple colored circle)
            brand_size = min(width, height) // 20
            brand_x = width - brand_size - 20
            brand_y = 20
            
            # Draw brand circle
            draw.ellipse(
                [brand_x, brand_y, brand_x + brand_size, brand_y + brand_size],
                fill=self.brand_colors["accent"],
                outline=self.brand_colors["primary"],
                width=2
            )
            
            # Add "BRAND" text inside the circle
            try:
                brand_font = ImageFont.truetype("arial.ttf", brand_size // 3)
            except:
                brand_font = ImageFont.load_default()
            
            brand_text = "BRAND"
            text_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = brand_x + (brand_size - text_width) // 2
            text_y = brand_y + (brand_size - text_height) // 2
            
            draw.text((text_x, text_y), brand_text, fill=(0, 0, 0), font=brand_font)
            
        except Exception as e:
            logger.error(f"Error adding simple brand indicator: {str(e)}")
    
    def _draw_text_with_outline(
        self,
        draw: ImageDraw.Draw,
        text: str,
        position: Tuple[int, int],
        font: ImageFont.ImageFont,
        fill_color: Tuple[int, int, int],
        outline_color: Tuple[int, int, int],
        outline_width: int = 2
    ):
        """
        Draw text with an outline for better readability.
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            position: Position tuple (x, y)
            font: Font to use
            fill_color: Text color
            outline_color: Outline color
            outline_width: Width of the outline
        """
        x, y = position
        
        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill_color)
    
    async def _translate_text_with_openai(self, text: str, target_language: str) -> str:
        """
        Translate text using OpenAI's API.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            Translated text or original text if translation fails
        """
        try:
            # Get OpenAI API key
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                logger.warning("OpenAI API key not found, returning original text")
                return text
            
            # Language code mapping
            language_names = {
                "es": "Spanish",
                "fr": "French", 
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "ja": "Japanese",
                "ko": "Korean",
                "zh": "Chinese"
            }
            
            target_lang_name = language_names.get(target_language, target_language)
            
            # Prepare the prompt for translation
            prompt = f"""Translate the following marketing message to {target_lang_name}. 
            Keep the marketing tone and impact. Make it sound natural and engaging in the target language.
            Only return the translated text, nothing else.
            
            Text to translate: "{text}"
            """
            
            # Call OpenAI API
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional marketing translator. Translate marketing messages while maintaining their impact and appeal."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"Translated '{text}' to '{translated_text}' in {target_lang_name}")
                    return translated_text
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    return text
                    
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text
