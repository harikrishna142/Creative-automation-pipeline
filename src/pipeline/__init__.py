"""
Creative Automation Pipeline

A comprehensive system for generating social media campaign assets using AI.
"""

from .creative_pipeline import CreativePipeline
from .models import (
    CampaignBrief, GeneratedCreative, CampaignOutput, 
    GenerationRequest, Product, AspectRatio, AssetInfo
)
from .asset_generator import AssetGenerator
from .template_engine import TemplateEngine
from .quality_checker import QualityChecker

__version__ = "1.0.0"
__all__ = [
    "CreativePipeline",
    "CampaignBrief",
    "GeneratedCreative", 
    "CampaignOutput",
    "GenerationRequest",
    "Product",
    "AspectRatio",
    "AssetInfo",
    "AssetGenerator",
    "TemplateEngine",
    "QualityChecker"
]

