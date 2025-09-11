"""
Campaign brief and asset models for the creative automation pipeline.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AspectRatio(str, Enum):
    """Supported aspect ratios for social media campaigns."""
    SQUARE = "1:1"
    VERTICAL = "9:16"
    HORIZONTAL = "16:9"


class ContentType(str, Enum):
    """Types of content that can be generated."""
    IMAGE = "image"
    VIDEO = "video"
    BOTH = "both"


class VideoFormat(str, Enum):
    """Supported video formats for social media."""
    YOUTUBE_SHORTS = "youtube_shorts"  # 9:16, up to 60 seconds
    INSTAGRAM_REELS = "instagram_reels"  # 9:16, up to 90 seconds
    TIKTOK = "tiktok"  # 9:16, up to 10 minutes
    STORY = "story"  # 9:16, up to 15 seconds


class Product(BaseModel):
    """Product information for campaign generation."""
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Product description")
    category: str = Field(..., description="Product category")
    price: Optional[float] = Field(None, description="Product price")
    features: List[str] = Field(default_factory=list, description="Key product features")
    target_demographic: Optional[str] = Field(None, description="Primary target demographic")


class CampaignBrief(BaseModel):
    """Campaign brief containing all necessary information for creative generation."""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_name: str = Field(..., description="Campaign name")
    products: List[Product] = Field(..., min_items=1, description="At least 1 product for the campaign")
    target_region: str = Field(..., description="Target market/region")
    target_audience: str = Field(..., description="Target audience description")
    campaign_message: str = Field(..., description="Main campaign message")
    brand_guidelines: Optional[Dict[str, Any]] = Field(None, description="Brand guidelines and constraints")
    aspect_ratios: List[AspectRatio] = Field(
        default=[AspectRatio.SQUARE, AspectRatio.VERTICAL, AspectRatio.HORIZONTAL],
        description="Required aspect ratios"
    )
    language: str = Field(default="en", description="Campaign language")
    additional_requirements: Optional[Dict[str, Any]] = Field(None, description="Additional campaign requirements")
    asset_params: Optional[Dict[str, Any]] = Field(None, description="Asset parameters including selected logos, avatars, and generation settings")
    
    # Video-specific fields
    content_type: ContentType = Field(default=ContentType.IMAGE, description="Type of content to generate")
    video_format: Optional[VideoFormat] = Field(None, description="Video format for social media")
    video_duration: Optional[int] = Field(15, description="Video duration in seconds")
    include_music: bool = Field(default=True, description="Include background music")
    include_voice_over: bool = Field(default=True, description="Include voice-over narration")


class AssetInfo(BaseModel):
    """Information about an asset (input or generated)."""
    asset_id: str = Field(..., description="Unique asset identifier")
    asset_type: str = Field(..., description="Type of asset (image, video, etc.)")
    file_path: str = Field(..., description="Path to the asset file")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Asset dimensions")
    aspect_ratio: Optional[AspectRatio] = Field(None, description="Asset aspect ratio")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional asset metadata")


class GeneratedCreative(BaseModel):
    """Generated creative asset with metadata."""
    creative_id: str = Field(..., description="Unique creative identifier")
    product_name: str = Field(..., description="Product this creative is for")
    aspect_ratio: AspectRatio = Field(..., description="Aspect ratio of the creative")
    file_path: str = Field(..., description="Path to the generated creative file")
    campaign_message: str = Field(..., description="Campaign message displayed on creative")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation process metadata")
    quality_score: Optional[float] = Field(None, description="Quality score (0-1)")
    s3_url: Optional[str] = Field(None, description="S3 URL of the uploaded creative")
    variation_num: Optional[int] = Field(None, description="Variation number for this creative")


class GeneratedVideo(BaseModel):
    """Information about a generated video asset."""
    video_id: str = Field(..., description="Unique video identifier")
    product_name: str = Field(..., description="Product this video is for")
    video_format: VideoFormat = Field(..., description="Video format")
    file_path: str = Field(..., description="Path to the generated video file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    duration: Optional[float] = Field(None, description="Video duration in seconds")
    resolution: Optional[Dict[str, int]] = Field(None, description="Video resolution")
    fps: Optional[int] = Field(None, description="Frames per second")
    has_music: bool = Field(default=False, description="Whether video includes background music")
    has_voice_over: bool = Field(default=False, description="Whether video includes voice-over")
    quality_score: Optional[float] = Field(None, description="Quality assessment score")
    generation_time: Optional[float] = Field(None, description="Time taken to generate in seconds")
    ai_model_used: Optional[str] = Field(None, description="AI model used for generation")
    s3_url: Optional[str] = Field(None, description="S3 URL of the uploaded video")


class CampaignOutput(BaseModel):
    """Complete campaign output with all generated creatives."""
    campaign_id: str = Field(..., description="Campaign identifier")
    campaign_name: str = Field(..., description="Campaign name")
    generated_creatives: List[GeneratedCreative] = Field(default_factory=list, description="All generated creatives")
    generated_videos: List[GeneratedVideo] = Field(default_factory=list, description="All generated videos")
    generation_summary: Dict[str, Any] = Field(..., description="Summary of generation process")
    output_directory: str = Field(..., description="Directory containing all outputs")
    total_creatives: int = Field(..., description="Total number of creatives generated")
    total_videos: int = Field(..., description="Total number of videos generated")
    success_rate: float = Field(..., description="Success rate of generation (0-1)")


class GenerationRequest(BaseModel):
    """Request for generating creatives."""
    campaign_brief: CampaignBrief = Field(..., description="Campaign brief")
    input_assets: List[AssetInfo] = Field(default_factory=list, description="Available input assets")
    force_regenerate: bool = Field(False, description="Force regeneration even if assets exist")
    quality_threshold: float = Field(0.7, description="Minimum quality threshold for generated assets")
