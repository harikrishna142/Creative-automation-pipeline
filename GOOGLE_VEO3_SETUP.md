# Google Veo 3 Setup Guide

This guide will help you set up Google Veo 3 for high-quality video generation in the Creative Automation Pipeline.

## Prerequisites

1. **Google AI Studio Account**: Sign up at [https://aistudio.google.com/](https://aistudio.google.com/)
2. **Google Cloud Project** (optional but recommended)

## Step 1: Get Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Step 2: Set Environment Variables

### Option A: Environment Variables (Recommended)

Set the following environment variables:

```bash
# Windows (PowerShell)
$env:GOOGLE_AI_API_KEY="your_api_key_here"

# Windows (Command Prompt)
set GOOGLE_AI_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_AI_API_KEY="your_api_key_here"
```

### Option B: Create .env File

Create a `.env` file in the project root:

```env
GOOGLE_AI_API_KEY=your_api_key_here
GOOGLE_CLOUD_PROJECT_ID=your_project_id_here
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Test the Setup

1. Launch the Streamlit UI:
   ```bash
   python launch_ui.py
   ```

2. Go to Campaign Builder
3. Select "Video Only" or "Both Images & Videos"
4. Enable "Use Google Veo 3"
5. Create a campaign and generate videos

## Features

### Google Veo 3 Capabilities

- **High-Quality Video Generation**: Creates professional, cinematic 8-second videos at 720p resolution
- **Advanced AI Prompts**: Understands complex product descriptions and campaign requirements
- **Native Audio Generation**: Automatically generates synchronized audio, music, and voice-overs
- **Image-to-Video**: Can animate product images as starting frames
- **Brand Integration**: Incorporates brand colors, messaging, and guidelines
- **Localization**: Adapts content for different languages and cultures
- **Cinematic Quality**: Professional lighting, camera movements, and composition

### Veo 3 Specifications

- **Duration**: Fixed at 8 seconds
- **Resolution**: 720p (1280x720)
- **Frame Rate**: 24fps
- **Audio**: Native audio generation with dialogue, music, and sound effects
- **Generation Time**: 1-6 minutes depending on complexity

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure your API key is set correctly
   - Check that the environment variable is loaded

2. **Generation Fails**
   - The system will automatically fall back to traditional video generation
   - Check your internet connection
   - Verify your API key has the necessary permissions

3. **Slow Generation**
   - Video generation can take 2-5 minutes depending on quality
   - Higher quality settings take longer
   - Check your internet connection speed

### API Limits

- Google Veo 3 has usage limits based on your account type
- Free tier has limited requests per day
- Consider upgrading for production use

## Advanced Configuration

### Custom Video Settings

You can customize video generation by modifying the `veo3_config` in the pipeline:

```python
veo3_config = {
    "api_key": "your_api_key",
    "project_id": "your_project_id",
    "location": "us-central1",
    "quality": "High",
    "duration": 15,
    "resolution": {"width": 1080, "height": 1920},
    "fps": 30
}
```

### Prompt Customization

The system automatically creates detailed prompts for Veo 3 based on:
- Product information
- Campaign messaging
- Target audience
- Brand guidelines
- Video format requirements

## Support

For issues with Google Veo 3:
- Check the [Google AI Studio documentation](https://ai.google.dev/docs)
- Review the [Veo 3 API documentation](https://ai.google.dev/docs/veo3)
- Contact Google AI support for API-specific issues

For issues with the Creative Automation Pipeline:
- Check the project README
- Review the error logs in the output directory
- Create an issue in the project repository
