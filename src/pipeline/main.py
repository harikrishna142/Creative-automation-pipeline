"""
Main CLI interface for the Creative Automation Pipeline.
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from .creative_pipeline import CreativePipeline
    from .models import CampaignBrief, GenerationRequest, Product, AspectRatio
except ImportError:
    # For standalone execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from creative_pipeline import CreativePipeline
    from models import CampaignBrief, GenerationRequest, Product, AspectRatio

console = Console()


@click.group()
def cli():
    """Creative Automation Pipeline CLI"""
    pass


@cli.command()
@click.option("--brief", "-b", required=True, help="Path to campaign brief file (JSON or YAML)")
@click.option("--output", "-o", default="output", help="Output directory for generated creatives")
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--assets", "-a", help="Path to input assets directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def generate(brief: str, output: str, config: Optional[str], assets: Optional[str], verbose: bool):
    """Generate creative assets from a campaign brief."""
    
    # Load configuration
    pipeline_config = load_config(config)
    
    # Load campaign brief
    campaign_brief = load_campaign_brief(brief)
    
    # Load input assets if provided
    input_assets = []
    if assets:
        input_assets = load_input_assets(assets)
    
    # Create generation request
    request = GenerationRequest(
        campaign_brief=campaign_brief,
        input_assets=input_assets
    )
    
    # Run the pipeline
    asyncio.run(run_pipeline(request, output, pipeline_config, verbose))


@cli.command()
@click.option("--output", "-o", default="output", help="Output directory to analyze")
def analyze(output: str):
    """Analyze generated creatives and show quality metrics."""
    
    output_path = Path(output)
    if not output_path.exists():
        console.print(f"[red]Output directory not found: {output}[/red]")
        return
    
    # Find all campaign directories
    campaign_dirs = [d for d in output_path.iterdir() if d.is_dir() and d.name != "assets"]
    
    if not campaign_dirs:
        console.print("[yellow]No campaign outputs found[/yellow]")
        return
    
    # Create analysis table
    table = Table(title="Campaign Analysis")
    table.add_column("Campaign ID", style="cyan")
    table.add_column("Campaign Name", style="magenta")
    table.add_column("Total Creatives", justify="right")
    table.add_column("Success Rate", justify="right")
    table.add_column("Avg Quality", justify="right")
    
    for campaign_dir in campaign_dirs:
        summary_file = campaign_dir / "generation_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
            
            # Calculate average quality
            avg_quality = calculate_average_quality(campaign_dir)
            
            table.add_row(
                summary.get("campaign_id", "Unknown"),
                campaign_dir.name,
                str(summary.get("total_generated", 0)),
                f"{summary.get('success_rate', 0):.1%}",
                f"{avg_quality:.2f}"
            )
    
    console.print(table)


@cli.command()
def example():
    """Generate example campaign briefs."""
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # Create example campaign briefs
    create_example_briefs(examples_dir)
    
    console.print(f"[green]Example campaign briefs created in {examples_dir}[/green]")
    console.print("You can use these as templates for your own campaigns.")


def load_config(config_path: Optional[str]) -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    
    default_config = {
        "ai_config": {
            "openai_api_key": None,
            "dalle_model": "dall-e-3",
            "fallback_mode": True
        },
        "template_config": {
            "default_font_size": 48,
            "text_color": (255, 255, 255),
            "text_outline_color": (0, 0, 0),
            "text_position": "bottom",
            "brand_colors": {
                "primary": (70, 130, 180),
                "secondary": (255, 255, 255),
                "accent": (255, 215, 0)
            }
        },
        "quality_config": {
            "min_resolution": (800, 800),
            "max_file_size": 10 * 1024 * 1024,
            "brand_colors": {
                "primary": (70, 130, 180),
                "secondary": (255, 255, 255),
                "accent": (255, 215, 0)
            },
            "prohibited_words": ["free", "win", "winner", "prize", "contest", "sweepstakes"],
            "required_elements": ["brand_logo", "product_name", "campaign_message"]
        }
    }
    
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                user_config = yaml.safe_load(f)
            else:
                user_config = json.load(f)
        
        # Merge with defaults
        default_config.update(user_config)
    
    return default_config


def load_campaign_brief(brief_path: str) -> CampaignBrief:
    """Load campaign brief from JSON or YAML file."""
    
    brief_file = Path(brief_path)
    if not brief_file.exists():
        raise FileNotFoundError(f"Campaign brief file not found: {brief_path}")
    
    with open(brief_file) as f:
        if brief_path.endswith('.yaml') or brief_path.endswith('.yml'):
            data = yaml.safe_load(f)
        else:
            data = json.load(f)
    
    return CampaignBrief(**data)


def load_input_assets(assets_dir: str) -> list:
    """Load input assets from directory."""
    
    assets_path = Path(assets_dir)
    if not assets_path.exists():
        console.print(f"[yellow]Assets directory not found: {assets_dir}[/yellow]")
        return []
    
    assets = []
    for asset_file in assets_path.iterdir():
        if asset_file.is_file() and asset_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            # Create basic asset info
            from .models import AssetInfo
            asset = AssetInfo(
                asset_id=str(asset_file.stem),
                asset_type="image",
                file_path=str(asset_file),
                metadata={"source": "input"}
            )
            assets.append(asset)
    
    return assets


async def run_pipeline(
    request: GenerationRequest,
    output_dir: str,
    config: Dict[str, Any],
    verbose: bool
):
    """Run the creative pipeline."""
    
    console.print(f"[blue]Starting creative generation for campaign: {request.campaign_brief.campaign_name}[/blue]")
    
    # Create pipeline
    pipeline = CreativePipeline(output_dir=output_dir, config=config)
    
    # Run with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating creatives...", total=None)
        
        try:
            result = await pipeline.process_campaign(request)
            
            progress.update(task, description="Generation completed!")
            
            # Display results
            console.print(f"\n[green]✓ Campaign generation completed![/green]")
            console.print(f"Campaign ID: {result.campaign_id}")
            console.print(f"Total creatives generated: {result.total_creatives}")
            console.print(f"Success rate: {result.success_rate:.1%}")
            console.print(f"Output directory: {result.output_directory}")
            
            # Show individual creatives
            if result.generated_creatives:
                table = Table(title="Generated Creatives")
                table.add_column("Product", style="cyan")
                table.add_column("Aspect Ratio", style="magenta")
                table.add_column("Quality Score", justify="right")
                table.add_column("File Path", style="green")
                
                for creative in result.generated_creatives:
                    quality = f"{creative.quality_score:.2f}" if creative.quality_score else "N/A"
                    table.add_row(
                        creative.product_name,
                        creative.aspect_ratio.value,
                        quality,
                        creative.file_path
                    )
                
                console.print(table)
            
            if result.generation_summary.get("errors"):
                console.print("\n[yellow]Warnings/Errors:[/yellow]")
                for error in result.generation_summary["errors"]:
                    console.print(f"  • {error}")
        
        except Exception as e:
            progress.update(task, description="Generation failed!")
            console.print(f"\n[red]✗ Generation failed: {str(e)}[/red]")
            if verbose:
                import traceback
                console.print(traceback.format_exc())


def calculate_average_quality(campaign_dir: Path) -> float:
    """Calculate average quality score for a campaign."""
    
    quality_scores = []
    
    # Look for creative files and extract quality scores
    for creative_file in campaign_dir.rglob("creative_*.jpg"):
        # Try to find metadata file
        metadata_file = creative_file.with_suffix(".json")
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    if "quality_score" in metadata:
                        quality_scores.append(metadata["quality_score"])
            except:
                pass
    
    return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0


def create_example_briefs(examples_dir: Path):
    """Create example campaign briefs."""
    
    # Example 1: Tech Products
    tech_brief = {
        "campaign_id": "tech_launch_2024",
        "campaign_name": "Tech Product Launch Campaign",
        "products": [
            {
                "name": "SmartPhone Pro",
                "description": "Latest flagship smartphone with advanced camera system",
                "category": "Electronics",
                "price": 999.99,
                "features": ["5G connectivity", "Triple camera system", "All-day battery"],
                "target_demographic": "Tech enthusiasts aged 25-45"
            },
            {
                "name": "Wireless Earbuds",
                "description": "Premium wireless earbuds with noise cancellation",
                "category": "Audio",
                "price": 199.99,
                "features": ["Active noise cancellation", "30-hour battery", "Water resistant"],
                "target_demographic": "Music lovers and professionals"
            }
        ],
        "target_region": "North America",
        "target_audience": "Tech-savvy consumers aged 25-45 with disposable income",
        "campaign_message": "Experience the future of technology today",
        "aspect_ratios": ["1:1", "9:16", "16:9"],
        "language": "en",
        "brand_guidelines": {
            "primary_color": "#4682B4",
            "secondary_color": "#FFFFFF",
            "accent_color": "#FFD700",
            "font_family": "Arial"
        }
    }
    
    # Example 2: Fashion Products
    fashion_brief = {
        "campaign_id": "fashion_spring_2024",
        "campaign_name": "Spring Fashion Collection",
        "products": [
            {
                "name": "Designer Handbag",
                "description": "Luxury leather handbag with modern design",
                "category": "Fashion",
                "price": 450.00,
                "features": ["Genuine leather", "Multiple compartments", "Adjustable strap"],
                "target_demographic": "Fashion-conscious women aged 25-40"
            },
            {
                "name": "Premium Watch",
                "description": "Elegant timepiece with Swiss movement",
                "category": "Accessories",
                "price": 750.00,
                "features": ["Swiss movement", "Sapphire crystal", "Water resistant"],
                "target_demographic": "Professionals and watch enthusiasts"
            }
        ],
        "target_region": "Europe",
        "target_audience": "Fashion-conscious consumers with high purchasing power",
        "campaign_message": "Elevate your style with timeless elegance",
        "aspect_ratios": ["1:1", "9:16", "16:9"],
        "language": "en",
        "brand_guidelines": {
            "primary_color": "#2C3E50",
            "secondary_color": "#ECF0F1",
            "accent_color": "#E74C3C",
            "font_family": "Helvetica"
        }
    }
    
    # Save example briefs
    with open(examples_dir / "tech_campaign.json", "w") as f:
        json.dump(tech_brief, f, indent=2)
    
    with open(examples_dir / "fashion_campaign.json", "w") as f:
        json.dump(fashion_brief, f, indent=2)
    
    # Create YAML versions
    with open(examples_dir / "tech_campaign.yaml", "w") as f:
        yaml.dump(tech_brief, f, default_flow_style=False, indent=2)
    
    with open(examples_dir / "fashion_campaign.yaml", "w") as f:
        yaml.dump(fashion_brief, f, default_flow_style=False, indent=2)


if __name__ == "__main__":
    cli()
