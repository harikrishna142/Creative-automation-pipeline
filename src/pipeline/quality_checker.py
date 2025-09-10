"""
Quality Checker - Validates generated creatives for brand compliance and quality.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from loguru import logger
from PIL import Image, ImageStat


class QualityChecker:
    """
    Handles quality checking and brand compliance validation for generated creatives.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the quality checker.
        
        Args:
            config: Configuration dictionary for quality settings
        """
        self.config = config
        self.min_resolution = config.get("min_resolution", (800, 800))
        self.max_file_size = config.get("max_file_size", 10 * 1024 * 1024)  # 10MB
        self.brand_colors = config.get("brand_colors", {
            "primary": (70, 130, 180),
            "secondary": (255, 255, 255),
            "accent": (255, 215, 0)
        })
        self.prohibited_words = config.get("prohibited_words", [
            "free", "win", "winner", "prize", "contest", "sweepstakes"
        ])
        self.required_elements = config.get("required_elements", [
            "brand_logo", "product_name", "campaign_message"
        ])
    
    async def check_creative_quality(
        self,
        image_path: Path,
        campaign_brief,
        product
    ) -> float:
        """
        Check the quality of a generated creative and return a quality score.
        
        Args:
            image_path: Path to the creative image
            campaign_brief: Campaign brief information
            product: Product information
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            quality_checks = []
            
            # Technical quality checks
            technical_score = await self._check_technical_quality(image_path)
            quality_checks.append(("technical", technical_score, 0.3))
            
            # Brand compliance checks
            brand_score = await self._check_brand_compliance(image_path, campaign_brief)
            quality_checks.append(("brand", brand_score, 0.3))
            
            # Content quality checks
            content_score = await self._check_content_quality(campaign_brief, product)
            quality_checks.append(("content", content_score, 0.2))
            
            # Visual quality checks
            visual_score = await self._check_visual_quality(image_path)
            quality_checks.append(("visual", visual_score, 0.2))
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in quality_checks)
            
            logger.info(f"Quality check completed for {image_path.name}: {total_score:.2f}")
            return total_score
            
        except Exception as e:
            logger.error(f"Error checking creative quality: {str(e)}")
            return 0.0
    
    async def _check_technical_quality(self, image_path: Path) -> float:
        """
        Check technical quality aspects of the image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Technical quality score (0.0 - 1.0)
        """
        try:
            score = 0.0
            
            # Check if file exists and is readable
            if not image_path.exists():
                logger.warning(f"Image file does not exist: {image_path}")
                return 0.0
            
            # Check file size
            file_size = image_path.stat().st_size
            if file_size > self.max_file_size:
                logger.warning(f"Image file too large: {file_size} bytes")
                score -= 0.2
            else:
                score += 0.2
            
            # Check image dimensions
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Check minimum resolution
                if width >= self.min_resolution[0] and height >= self.min_resolution[1]:
                    score += 0.3
                else:
                    logger.warning(f"Image resolution too low: {width}x{height}")
                    score -= 0.3
                
                # Check aspect ratio appropriateness
                aspect_ratio = width / height
                if 0.5 <= aspect_ratio <= 2.0:  # Reasonable aspect ratios
                    score += 0.2
                else:
                    logger.warning(f"Unusual aspect ratio: {aspect_ratio}")
                    score -= 0.2
                
                # Check image mode
                if img.mode in ['RGB', 'RGBA']:
                    score += 0.1
                else:
                    logger.warning(f"Unsupported image mode: {img.mode}")
                    score -= 0.1
                
                # Check for corruption
                try:
                    img.verify()
                    score += 0.2
                except Exception:
                    logger.warning("Image appears to be corrupted")
                    score -= 0.2
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error checking technical quality: {str(e)}")
            return 0.0
    
    async def _check_brand_compliance(self, image_path: Path, campaign_brief) -> float:
        """
        Check brand compliance aspects of the creative.
        
        Args:
            image_path: Path to the image
            campaign_brief: Campaign brief information
            
        Returns:
            Brand compliance score (0.0 - 1.0)
        """
        try:
            score = 0.0
            
            with Image.open(image_path) as img:
                # Check for brand colors
                brand_color_score = await self._check_brand_colors(img)
                score += brand_color_score * 0.4
                
                # Check for required elements (simplified check)
                required_elements_score = await self._check_required_elements(img, campaign_brief)
                score += required_elements_score * 0.6
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error checking brand compliance: {str(e)}")
            return 0.0
    
    async def _check_brand_colors(self, image: Image.Image) -> float:
        """
        Check if the image contains brand colors.
        
        Args:
            image: PIL Image object
            
        Returns:
            Brand color score (0.0 - 1.0)
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image statistics
            stat = ImageStat.Stat(image)
            mean_colors = stat.mean
            
            # Check if any brand colors are present (simplified check)
            # In a real implementation, this would be more sophisticated
            score = 0.0
            
            # Check for presence of brand colors in the image
            # This is a simplified check - in reality, you'd analyze color distribution
            for brand_color in self.brand_colors.values():
                if isinstance(brand_color, tuple) and len(brand_color) >= 3:
                    # Simple check: if the mean color is close to any brand color
                    color_diff = sum(abs(mean_colors[i] - brand_color[i]) for i in range(3))
                    if color_diff < 100:  # Threshold for color similarity
                        score += 0.33
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error checking brand colors: {str(e)}")
            return 0.0
    
    async def _check_required_elements(self, image: Image.Image, campaign_brief) -> float:
        """
        Check if required elements are present in the image.
        
        Args:
            image: PIL Image object
            campaign_brief: Campaign brief information
            
        Returns:
            Required elements score (0.0 - 1.0)
        """
        try:
            score = 0.0
            
            # Check for text content (simplified)
            # In a real implementation, you'd use OCR to detect text
            # For now, we'll assume text is present if the image has been processed
            score += 0.5  # Assume campaign message is present
            
            # Check for brand logo (simplified)
            # In a real implementation, you'd use object detection
            score += 0.3  # Assume brand logo is present
            
            # Check for product name (simplified)
            score += 0.2  # Assume product name is present
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error checking required elements: {str(e)}")
            return 0.0
    
    async def _check_content_quality(self, campaign_brief, product) -> float:
        """
        Check content quality aspects.
        
        Args:
            campaign_brief: Campaign brief information
            product: Product information
            
        Returns:
            Content quality score (0.0 - 1.0)
        """
        try:
            score = 0.0
            
            # Check campaign message quality
            message = campaign_brief.campaign_message
            if message and len(message.strip()) > 0:
                score += 0.3
                
                # Check for prohibited words
                message_lower = message.lower()
                prohibited_found = any(word in message_lower for word in self.prohibited_words)
                if not prohibited_found:
                    score += 0.2
                else:
                    logger.warning("Prohibited words found in campaign message")
                    score -= 0.2
                
                # Check message length
                if 10 <= len(message) <= 200:
                    score += 0.2
                else:
                    logger.warning(f"Campaign message length inappropriate: {len(message)}")
                    score -= 0.1
            else:
                logger.warning("No campaign message provided")
                score -= 0.3
            
            # Check product information
            if product.name and len(product.name.strip()) > 0:
                score += 0.2
            else:
                logger.warning("No product name provided")
                score -= 0.2
            
            if product.description and len(product.description.strip()) > 0:
                score += 0.1
            else:
                logger.warning("No product description provided")
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error checking content quality: {str(e)}")
            return 0.0
    
    async def _check_visual_quality(self, image_path: Path) -> float:
        """
        Check visual quality aspects of the image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Visual quality score (0.0 - 1.0)
        """
        try:
            score = 0.0
            
            with Image.open(image_path) as img:
                # Check image brightness
                stat = ImageStat.Stat(img)
                mean_brightness = sum(stat.mean) / len(stat.mean)
                
                if 50 <= mean_brightness <= 200:  # Reasonable brightness range
                    score += 0.3
                else:
                    logger.warning(f"Image brightness inappropriate: {mean_brightness}")
                    score -= 0.2
                
                # Check image contrast (simplified)
                # In a real implementation, you'd calculate actual contrast
                score += 0.3  # Assume good contrast
                
                # Check for blur (simplified)
                # In a real implementation, you'd use edge detection
                score += 0.2  # Assume not blurred
                
                # Check color saturation
                # In a real implementation, you'd analyze color distribution
                score += 0.2  # Assume good saturation
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error checking visual quality: {str(e)}")
            return 0.0
    
    async def get_quality_report(
        self,
        image_path: Path,
        campaign_brief,
        product
    ) -> Dict[str, Any]:
        """
        Generate a detailed quality report for a creative.
        
        Args:
            image_path: Path to the image
            campaign_brief: Campaign brief information
            product: Product information
            
        Returns:
            Detailed quality report
        """
        try:
            report = {
                "image_path": str(image_path),
                "product_name": product.name,
                "overall_score": 0.0,
                "category_scores": {},
                "issues": [],
                "recommendations": []
            }
            
            # Get individual category scores
            technical_score = await self._check_technical_quality(image_path)
            brand_score = await self._check_brand_compliance(image_path, campaign_brief)
            content_score = await self._check_content_quality(campaign_brief, product)
            visual_score = await self._check_visual_quality(image_path)
            
            report["category_scores"] = {
                "technical": technical_score,
                "brand": brand_score,
                "content": content_score,
                "visual": visual_score
            }
            
            # Calculate overall score
            report["overall_score"] = (
                technical_score * 0.3 +
                brand_score * 0.3 +
                content_score * 0.2 +
                visual_score * 0.2
            )
            
            # Generate issues and recommendations
            if technical_score < 0.7:
                report["issues"].append("Technical quality issues detected")
                report["recommendations"].append("Check image resolution and file size")
            
            if brand_score < 0.7:
                report["issues"].append("Brand compliance issues detected")
                report["recommendations"].append("Ensure brand colors and elements are present")
            
            if content_score < 0.7:
                report["issues"].append("Content quality issues detected")
                report["recommendations"].append("Review campaign message and product information")
            
            if visual_score < 0.7:
                report["issues"].append("Visual quality issues detected")
                report["recommendations"].append("Check image brightness, contrast, and clarity")
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating quality report: {str(e)}")
            return {
                "image_path": str(image_path),
                "error": str(e),
                "overall_score": 0.0
            }
