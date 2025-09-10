# FDE Creative Automation Pipeline

## Overview
This project implements a comprehensive creative automation pipeline for scalable social ad campaigns, designed to help global consumer goods companies rapidly generate and localize creative assets using AI-powered automation.

## 🎯 Business Goals Addressed
- **Accelerate Campaign Velocity**: Rapidly ideate, produce, approve, and launch more campaigns per month
- **Ensure Brand Consistency**: Maintain global brand guidelines and voice across all markets and languages
- **Maximize Relevance & Personalization**: Adapt messaging, offers, and creative to resonate with local cultures
- **Optimize Marketing ROI**: Increase campaign efficiency and performance metrics
- **Gain Actionable Insights**: Track effectiveness at scale and learn what drives best outcomes

## 🏗️ Project Structure
```
Adobe FDE/
├── docs/                    # Documentation and presentations
│   ├── architecture/        # Architecture diagrams and designs
│   │   └── system_architecture.md
│   └── presentations/       # Presentation materials
│       └── roadmap.md
├── src/                     # Source code
│   ├── pipeline/           # Creative automation pipeline
│   │   ├── __init__.py
│   │   ├── main.py         # CLI interface
│   │   ├── models.py       # Data models
│   │   ├── creative_pipeline.py  # Main pipeline
│   │   ├── asset_generator.py    # AI image generation
│   │   ├── template_engine.py    # Template application
│   │   └── quality_checker.py    # Quality validation
│   ├── agents/             # AI-driven monitoring agents
│   │   ├── __init__.py
│   │   ├── monitoring_agent.py   # Pipeline monitoring
│   │   └── communication_templates.py  # Stakeholder comms
│   └── utils/              # Utility functions
├── examples/               # Example campaign briefs and outputs
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ✅ Tasks Completed
- [x] **Task 1**: High-Level Architecture Diagram and Roadmap
- [x] **Task 2**: Creative Automation Pipeline (Proof of Concept)
- [x] **Task 3**: Agentic System Design & Stakeholder Communication
- [x] **Bonus**: Google Veo 3 Integration for Advanced Video Generation
- [x] **Bonus**: AWS S3 Storage Integration for Campaign Data and Assets

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (optional, for AI image generation)
- Virtual environment (already set up as `venv1`)

### Installation
1. **Activate the virtual environment:**
   ```bash
   # Windows
   venv1\Scripts\activate
   
   # macOS/Linux
   source venv1/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional):**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

### 🎨 Adobe Creative Studio UI (Recommended)

**Launch the modern web interface:**
```bash
python launch_ui.py
```

This opens a beautiful, Adobe-inspired web interface with:
- **Dashboard**: Overview of campaigns and metrics
- **Campaign Builder**: Visual campaign creation
- **Creative Gallery**: Browse and download generated assets
- **Analytics**: Performance metrics and charts
- **Settings**: Configure AI and quality settings

The UI will open at: http://localhost:8501

## 🤖 Google Veo 3 Integration

The pipeline now includes **Google Veo 3** for advanced AI-powered video generation:

### Setup Google Veo 3

1. **Get your API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Set environment variable**:
   ```bash
   # Windows
   $env:GOOGLE_AI_API_KEY="your_api_key_here"
   
   # Linux/Mac
   export GOOGLE_AI_API_KEY="your_api_key_here"
   ```
3. **Enable in UI**: Check "Use Google Veo 3" in the Campaign Builder

### Veo 3 Features

- **🎬 High-Quality Videos**: Professional, cinematic 8-second videos at 720p resolution
- **🎨 Intelligent Composition**: Automatic shot selection and transitions
- **🎵 Native Audio**: AI-generated dialogue, music, and sound effects
- **📸 Image-to-Video**: Animate product images as starting frames
- **🌍 Localization**: Content adapted for different languages and cultures
- **⚡ Fast Generation**: 1-6 minutes generation time

See [GOOGLE_VEO3_SETUP.md](GOOGLE_VEO3_SETUP.md) for detailed setup instructions.

### 💻 Command Line Usage

1. **Generate example campaign briefs:**
   ```bash
   python src/pipeline/main.py example
   ```

2. **Run the pipeline with a campaign brief:**
   ```bash
   python src/pipeline/main.py generate -b examples/tech_campaign.json -o output
   ```

3. **Analyze generated results:**
   ```bash
   python src/pipeline/main.py analyze -o output
   ```

### 🎯 Quick Demo
```bash
python demo.py
```

## 📋 Campaign Brief Format

The pipeline accepts campaign briefs in JSON or YAML format. Here's the structure:

```json
{
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
    "accent_color": "#FFD700"
  }
}
```

## 🎨 Adobe Creative Studio UI Features

### 🏠 Dashboard
- **Real-time Metrics**: Campaign count, creative generation, success rates
- **Recent Campaigns**: Quick overview of latest campaigns
- **Quick Actions**: Start generation, create new campaigns
- **Pipeline Status**: Live monitoring of system health

### 🎯 Campaign Builder
- **Visual Form Interface**: Intuitive campaign creation
- **Dynamic Product Management**: Add/remove products easily
- **Brand Guidelines**: Color picker and style settings
- **Aspect Ratio Selection**: Choose from 1:1, 9:16, 16:9
- **Real-time Preview**: See campaign details as you build

### 🖼️ Creative Gallery
- **Campaign Browser**: Navigate through all campaigns
- **Product Organization**: View creatives by product
- **Aspect Ratio Grid**: See all format variations
- **Download Manager**: One-click download of any creative
- **Preview Cards**: Beautiful hover effects and styling

### 📊 Analytics Dashboard
- **Performance Charts**: Interactive Plotly visualizations
- **Success Rate Trends**: Track pipeline performance over time
- **Volume Metrics**: Campaign and creative generation stats
- **Quality Scores**: Monitor creative quality trends
- **Cost Analysis**: Track generation costs and efficiency

### ⚙️ Settings & Configuration
- **AI Configuration**: OpenAI API key and model settings
- **Quality Thresholds**: Set minimum quality scores
- **Brand Guidelines**: Default colors and fonts
- **System Information**: Version and status details

## 🎨 Generated Outputs

The pipeline generates creatives organized by:
- **Campaign ID** → **Product Name** → **Aspect Ratio**
- **Quality scores** for each generated creative
- **Generation metadata** and performance metrics
- **Summary reports** with success rates and analytics

### Supported Aspect Ratios
- **1:1 (Square)**: Instagram posts, Facebook posts
- **9:16 (Vertical)**: Instagram Stories, TikTok, YouTube Shorts
- **16:9 (Horizontal)**: YouTube thumbnails, LinkedIn posts

## 🤖 AI Features

### Asset Generation
- **OpenAI DALL-E Integration**: High-quality product image generation
- **Fallback Systems**: Mock images and simple graphics when AI unavailable
- **Smart Prompting**: Context-aware prompts based on product and campaign details

### Quality Assurance
- **Brand Compliance Checking**: Automated validation of brand guidelines
- **Content Moderation**: Detection of prohibited words and inappropriate content
- **Technical Quality**: Resolution, file size, and format validation
- **Visual Quality**: Brightness, contrast, and clarity assessment

### Monitoring & Alerts
- **Real-time Monitoring**: Track pipeline health and performance
- **Intelligent Alerts**: AI-powered anomaly detection and issue identification
- **Stakeholder Communications**: Automated, context-aware notifications
- **Performance Analytics**: Comprehensive metrics and trend analysis

## 📊 Key Features

### Creative Pipeline
- ✅ **Multi-Product Support**: Handle campaigns with 2+ products
- ✅ **Multi-Format Generation**: Create assets for all major social platforms
- ✅ **Brand Consistency**: Automated brand guideline enforcement
- ✅ **Quality Scoring**: Comprehensive quality assessment (0-1 scale)
- ✅ **Localization Ready**: Framework for multi-language support

### Monitoring & Communication
- ✅ **AI-Driven Monitoring**: Intelligent pipeline health monitoring
- ✅ **Stakeholder Alerts**: Context-aware communications for different audiences
- ✅ **Performance Tracking**: Real-time metrics and trend analysis
- ✅ **Incident Management**: Automated incident detection and reporting

### Technical Excellence
- ✅ **Modular Architecture**: Clean, extensible codebase
- ✅ **Error Handling**: Robust error handling and fallback mechanisms
- ✅ **Logging**: Comprehensive logging and debugging support
- ✅ **Documentation**: Extensive documentation and examples

## 🔧 Configuration

### Pipeline Configuration
```python
config = {
    "ai_config": {
        "openai_api_key": "your_key_here",
        "dalle_model": "dall-e-3",
        "fallback_mode": True
    },
    "template_config": {
        "default_font_size": 48,
        "text_color": (255, 255, 255),
        "brand_colors": {
            "primary": (70, 130, 180),
            "accent": (255, 215, 0)
        }
    },
    "quality_config": {
        "min_resolution": (800, 800),
        "min_quality_score": 0.7,
        "prohibited_words": ["free", "win", "prize"]
    }
}
```

## 📈 Performance Metrics

The pipeline tracks and reports:
- **Success Rate**: Percentage of successfully generated creatives
- **Generation Time**: Average time per creative generation
- **Quality Scores**: Average quality across all generated assets
- **API Reliability**: Success rate of external AI service calls
- **Resource Utilization**: System resource usage and efficiency

## 🚨 Monitoring & Alerts

### Alert Types
- **Performance Degradation**: Success rate or speed issues
- **API Failures**: External service connectivity problems
- **Quality Threshold Breach**: Generated content below standards
- **Resource Exhaustion**: System capacity issues
- **Brand Compliance Issues**: Content not meeting brand guidelines

### Stakeholder Communications
- **Executive Leadership**: High-level business impact summaries
- **Creative Teams**: Quality metrics and creative performance
- **IT Teams**: Technical details and system health
- **Client Communications**: Professional delay notifications and updates

## ☁️ AWS S3 Storage Integration

The pipeline includes comprehensive AWS S3 storage integration for scalable cloud storage of campaign data, assets, and generated creatives.

### S3 Storage Features
- **Campaign Data Storage**: Automatic upload of campaign briefs and outputs to S3
- **Asset Management**: Upload and organize brand assets, logos, and avatars
- **Creative Storage**: Store all generated images and videos in organized S3 structure
- **Metadata Tracking**: Comprehensive metadata for all stored files
- **Presigned URLs**: Generate temporary access URLs for secure file sharing

### S3 Configuration
Set the following environment variables for S3 integration:

```bash
# Required AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here

# S3 Configuration
S3_BUCKET_NAME=creative-automation-pipeline
S3_REGION=us-east-1
S3_PREFIX=campaigns
```

### S3 Storage Structure
```
s3://your-bucket/
├── campaigns/
│   ├── campaign_20240101_120000/
│   │   ├── campaign_brief.json
│   │   ├── campaign_output.json
│   │   ├── creatives/
│   │   │   └── product_name/
│   │   │       ├── 1x1/
│   │   │       ├── 9x16/
│   │   │       └── 16x9/
│   │   └── videos/
│   │       └── product_name/
│   │           └── format/
│   └── assets/
│       ├── brand_logo/
│       ├── avatar/
│       ├── background/
│       └── theme/
```

### S3 Management UI
The Streamlit interface includes a dedicated S3 Management page with:
- **Storage Overview**: Bucket usage statistics and file counts
- **Upload Interface**: Drag-and-drop file upload to S3
- **Download Tools**: Download files from S3 with progress tracking
- **Connection Testing**: Verify S3 connectivity and permissions
- **URL Generation**: Create presigned URLs for secure sharing

### Benefits of S3 Integration
- **Scalability**: Handle large volumes of campaign data and assets
- **Durability**: 99.999999999% (11 9's) durability for stored objects
- **Accessibility**: Global access to campaign assets and creatives
- **Cost Efficiency**: Pay only for storage used with lifecycle policies
- **Integration**: Seamless integration with other AWS services
- **Security**: Fine-grained access controls and encryption options

## 🧪 Testing

Run the example campaigns to test the pipeline:

```bash
# Generate example briefs
python src/pipeline/main.py example

# Test with tech campaign
python src/pipeline/main.py generate -b examples/tech_campaign.json -v

# Test with fashion campaign  
python src/pipeline/main.py generate -b examples/fashion_campaign.yaml -v

# Analyze results
python src/pipeline/main.py analyze
```

## 📚 Documentation

- **Architecture**: `docs/architecture/system_architecture.md`
- **Roadmap**: `docs/presentations/roadmap.md`
- **API Reference**: See docstrings in source code
- **Examples**: `examples/` directory with sample campaigns

## 🔮 Future Enhancements

### Planned Features
- **Video Generation**: Support for video creative assets
- **Advanced Localization**: Multi-language text generation
- **A/B Testing**: Automated creative variant testing
- **Performance Optimization**: ML-based creative optimization
- **Integration APIs**: RESTful APIs for external system integration

### Scalability Improvements
- **Cloud Deployment**: Kubernetes and container orchestration
- **Microservices**: Service decomposition for better scalability
- **Caching**: Redis-based caching for improved performance
- **CDN Integration**: Global content delivery optimization

## 🤝 Contributing

This is a proof-of-concept implementation for the FDE take-home exercise. Key design decisions:

1. **Modular Architecture**: Clean separation of concerns for maintainability
2. **AI Integration**: Robust integration with external AI services
3. **Quality Focus**: Comprehensive quality assurance and validation
4. **Monitoring**: Intelligent monitoring and stakeholder communication
5. **Extensibility**: Framework designed for future enhancements

## 📞 Support

For questions about this implementation:
- Review the comprehensive documentation in `docs/`
- Check example campaigns in `examples/`
- Examine the source code for detailed implementation details
- Run the pipeline with verbose logging (`-v` flag) for debugging

---

**Note**: This is a proof-of-concept implementation demonstrating technical approach, problem-solving capabilities, and integration of creative technologies for the FDE take-home exercise.
