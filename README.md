# FDE Creative Automation Pipeline

## Overview
This project implements a comprehensive creative automation pipeline for scalable social ad campaigns, designed to help global consumer goods companies rapidly generate and localize creative assets using AI-powered automation.



##  Project Structure
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



## Quick Start

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

3. **Set up environment variables 
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

###  Adobe Creative Studio UI 

**Launch the modern web interface:**
```bash
streamlit run streamlit_app.py
```

This opens a beautiful, Adobe-inspired web interface with:
- **Dashboard**: Overview of campaigns and metrics
- **Campaign Builder**: Visual campaign creation
- **Creative Gallery**: Browse and download generated assets
- **Analytics**: Performance metrics and charts
- **Settings**: Configure AI and quality settings

The UI will open at: http://localhost:8501

##  Google Veo 3 Integration

The pipeline  includes **Google Veo 3** for advanced AI-powered video generation But requires tier1  subscritpion for api:

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



##  Campaign Brief Format

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
s




## ☁ AWS S3 Storage Integration

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




---

**Acknowledgement**: This is a proof-of-concept implementation demonstrating FDE take-home exercise.
