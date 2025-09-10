"""
AI-Driven Monitoring Agent for Creative Automation Pipeline

This agent monitors the creative automation pipeline, tracks performance metrics,
and generates human-readable alerts and communications for stakeholders.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from loguru import logger
import openai
from openai import AsyncOpenAI


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts the agent can generate."""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    API_FAILURE = "api_failure"
    QUALITY_THRESHOLD_BREACH = "quality_threshold_breach"
    MISSING_ASSETS = "missing_assets"
    GENERATION_DELAY = "generation_delay"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    BRAND_COMPLIANCE_ISSUE = "brand_compliance_issue"


@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    description: str
    timestamp: datetime
    campaign_id: Optional[str] = None
    product_name: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    resolved: bool = False


@dataclass
class PipelineMetrics:
    """Pipeline performance metrics."""
    timestamp: datetime
    total_campaigns_processed: int
    total_creatives_generated: int
    average_generation_time: float
    success_rate: float
    quality_score_average: float
    api_calls_made: int
    api_failures: int
    active_campaigns: int
    queue_depth: int
    resource_utilization: Dict[str, float]


class MonitoringAgent:
    """
    AI-driven monitoring agent that tracks pipeline health and generates intelligent alerts.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the monitoring agent.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        self.openai_client = AsyncOpenAI(api_key=config.get("openai_api_key"))
        self.alert_history: List[Alert] = []
        self.metrics_history: List[PipelineMetrics] = []
        
        # Monitoring thresholds
        self.thresholds = {
            "min_success_rate": 0.85,
            "max_generation_time": 300,  # 5 minutes
            "min_quality_score": 0.7,
            "max_api_failure_rate": 0.1,
            "max_queue_depth": 50,
            "max_resource_utilization": 0.8
        }
        
        # Alert templates for different scenarios
        self.alert_templates = {
            AlertType.PERFORMANCE_DEGRADATION: {
                "title": "Pipeline Performance Degradation Detected",
                "description": "The creative automation pipeline is experiencing performance issues."
            },
            AlertType.API_FAILURE: {
                "title": "AI Service API Failure",
                "description": "External AI service API calls are failing."
            },
            AlertType.QUALITY_THRESHOLD_BREACH: {
                "title": "Quality Threshold Breach",
                "description": "Generated creatives are falling below quality standards."
            },
            AlertType.MISSING_ASSETS: {
                "title": "Insufficient Creative Variants",
                "description": "Campaign is missing required creative variants."
            },
            AlertType.GENERATION_DELAY: {
                "title": "Campaign Generation Delay",
                "description": "Campaign generation is taking longer than expected."
            },
            AlertType.RESOURCE_EXHAUSTION: {
                "title": "Resource Exhaustion Warning",
                "description": "System resources are approaching capacity limits."
            },
            AlertType.BRAND_COMPLIANCE_ISSUE: {
                "title": "Brand Compliance Issue",
                "description": "Generated creatives are not meeting brand guidelines."
            }
        }
    
    async def monitor_pipeline(self, pipeline_data: Dict[str, Any]) -> List[Alert]:
        """
        Monitor pipeline health and generate alerts.
        
        Args:
            pipeline_data: Current pipeline state and metrics
            
        Returns:
            List of generated alerts
        """
        try:
            # Extract metrics from pipeline data
            metrics = self._extract_metrics(pipeline_data)
            self.metrics_history.append(metrics)
            
            # Keep only last 100 metrics for analysis
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            # Generate alerts based on current metrics and trends
            alerts = []
            
            # Check various conditions
            alerts.extend(await self._check_performance_metrics(metrics))
            alerts.extend(await self._check_api_health(metrics))
            alerts.extend(await self._check_quality_metrics(metrics))
            alerts.extend(await self._check_resource_utilization(metrics))
            alerts.extend(await self._check_campaign_completion(metrics))
            
            # Use AI to generate intelligent insights
            ai_insights = await self._generate_ai_insights(metrics, alerts)
            if ai_insights:
                alerts.extend(ai_insights)
            
            # Add new alerts to history
            self.alert_history.extend(alerts)
            
            # Keep only last 1000 alerts
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error in pipeline monitoring: {str(e)}")
            return []
    
    async def generate_stakeholder_communication(
        self,
        alert: Alert,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable communication for stakeholders.
        
        Args:
            alert: The alert to communicate
            context: Additional context about the situation
            
        Returns:
            Human-readable communication text
        """
        try:
            # Prepare context for AI
            context_prompt = self._prepare_communication_context(alert, context)
            
            # Generate communication using AI
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional communication specialist for a creative automation platform. 
                        Generate clear, concise, and actionable communications for business stakeholders. 
                        Focus on business impact, root causes, and next steps. Use a professional but accessible tone."""
                    },
                    {
                        "role": "user",
                        "content": context_prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating stakeholder communication: {str(e)}")
            return self._generate_fallback_communication(alert, context)
    
    async def generate_delay_notification(
        self,
        campaign_id: str,
        delay_reason: str,
        estimated_resolution: str
    ) -> str:
        """
        Generate a delay notification email for customer leadership.
        
        Args:
            campaign_id: Campaign experiencing delay
            delay_reason: Reason for the delay
            estimated_resolution: Estimated time to resolution
            
        Returns:
            Formatted email content
        """
        try:
            email_prompt = f"""
            Generate a professional email to customer leadership explaining a campaign delay.
            
            Campaign ID: {campaign_id}
            Delay Reason: {delay_reason}
            Estimated Resolution: {estimated_resolution}
            
            The email should:
            1. Acknowledge the delay professionally
            2. Explain the root cause in business terms
            3. Provide a clear timeline for resolution
            4. Offer alternative solutions if available
            5. Reassure about quality and future prevention
            
            Tone: Professional, transparent, solution-oriented
            Length: 2-3 paragraphs
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a customer success manager writing to executive leadership. 
                        Be transparent about issues while maintaining confidence in the solution. 
                        Focus on business impact and resolution timeline."""
                    },
                    {
                        "role": "user",
                        "content": email_prompt
                    }
                ],
                max_tokens=400,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating delay notification: {str(e)}")
            return self._generate_fallback_delay_email(campaign_id, delay_reason, estimated_resolution)
    
    def _extract_metrics(self, pipeline_data: Dict[str, Any]) -> PipelineMetrics:
        """Extract metrics from pipeline data."""
        
        return PipelineMetrics(
            timestamp=datetime.now(),
            total_campaigns_processed=pipeline_data.get("total_campaigns", 0),
            total_creatives_generated=pipeline_data.get("total_creatives", 0),
            average_generation_time=pipeline_data.get("avg_generation_time", 0),
            success_rate=pipeline_data.get("success_rate", 1.0),
            quality_score_average=pipeline_data.get("avg_quality_score", 0.8),
            api_calls_made=pipeline_data.get("api_calls", 0),
            api_failures=pipeline_data.get("api_failures", 0),
            active_campaigns=pipeline_data.get("active_campaigns", 0),
            queue_depth=pipeline_data.get("queue_depth", 0),
            resource_utilization=pipeline_data.get("resource_utilization", {})
        )
    
    async def _check_performance_metrics(self, metrics: PipelineMetrics) -> List[Alert]:
        """Check performance-related metrics and generate alerts."""
        
        alerts = []
        
        # Check success rate
        if metrics.success_rate < self.thresholds["min_success_rate"]:
            alert = Alert(
                alert_id=f"perf_{datetime.now().timestamp()}",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                level=AlertLevel.WARNING,
                title=self.alert_templates[AlertType.PERFORMANCE_DEGRADATION]["title"],
                description=f"Success rate has dropped to {metrics.success_rate:.1%}, below threshold of {self.thresholds['min_success_rate']:.1%}",
                timestamp=datetime.now(),
                metrics={"success_rate": metrics.success_rate},
                recommendations=[
                    "Review recent campaign briefs for quality issues",
                    "Check AI service API health",
                    "Verify input asset quality"
                ]
            )
            alerts.append(alert)
        
        # Check generation time
        if metrics.average_generation_time > self.thresholds["max_generation_time"]:
            alert = Alert(
                alert_id=f"time_{datetime.now().timestamp()}",
                alert_type=AlertType.GENERATION_DELAY,
                level=AlertLevel.WARNING,
                title=self.alert_templates[AlertType.GENERATION_DELAY]["title"],
                description=f"Average generation time is {metrics.average_generation_time:.1f}s, exceeding threshold of {self.thresholds['max_generation_time']}s",
                timestamp=datetime.now(),
                metrics={"generation_time": metrics.average_generation_time},
                recommendations=[
                    "Check system resource utilization",
                    "Review queue processing efficiency",
                    "Consider scaling up AI service capacity"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _check_api_health(self, metrics: PipelineMetrics) -> List[Alert]:
        """Check API health and generate alerts."""
        
        alerts = []
        
        if metrics.api_calls_made > 0:
            failure_rate = metrics.api_failures / metrics.api_calls_made
            
            if failure_rate > self.thresholds["max_api_failure_rate"]:
                alert = Alert(
                    alert_id=f"api_{datetime.now().timestamp()}",
                    alert_type=AlertType.API_FAILURE,
                    level=AlertLevel.ERROR,
                    title=self.alert_templates[AlertType.API_FAILURE]["title"],
                    description=f"API failure rate is {failure_rate:.1%}, exceeding threshold of {self.thresholds['max_api_failure_rate']:.1%}",
                    timestamp=datetime.now(),
                    metrics={"failure_rate": failure_rate, "api_calls": metrics.api_calls_made},
                    recommendations=[
                        "Check AI service provider status",
                        "Verify API key validity and quotas",
                        "Implement retry logic with exponential backoff"
                    ]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _check_quality_metrics(self, metrics: PipelineMetrics) -> List[Alert]:
        """Check quality-related metrics and generate alerts."""
        
        alerts = []
        
        if metrics.quality_score_average < self.thresholds["min_quality_score"]:
            alert = Alert(
                alert_id=f"quality_{datetime.now().timestamp()}",
                alert_type=AlertType.QUALITY_THRESHOLD_BREACH,
                level=AlertLevel.WARNING,
                title=self.alert_templates[AlertType.QUALITY_THRESHOLD_BREACH]["title"],
                description=f"Average quality score is {metrics.quality_score_average:.2f}, below threshold of {self.thresholds['min_quality_score']:.2f}",
                timestamp=datetime.now(),
                metrics={"quality_score": metrics.quality_score_average},
                recommendations=[
                    "Review brand compliance rules",
                    "Check template quality and consistency",
                    "Analyze recent campaign briefs for clarity"
                ]
            )
            alerts.append(alert)
        
        return alerts
    
    async def _check_resource_utilization(self, metrics: PipelineMetrics) -> List[Alert]:
        """Check resource utilization and generate alerts."""
        
        alerts = []
        
        for resource, utilization in metrics.resource_utilization.items():
            if utilization > self.thresholds["max_resource_utilization"]:
                alert = Alert(
                    alert_id=f"resource_{resource}_{datetime.now().timestamp()}",
                    alert_type=AlertType.RESOURCE_EXHAUSTION,
                    level=AlertLevel.WARNING,
                    title=self.alert_templates[AlertType.RESOURCE_EXHAUSTION]["title"],
                    description=f"{resource} utilization is {utilization:.1%}, exceeding threshold of {self.thresholds['max_resource_utilization']:.1%}",
                    timestamp=datetime.now(),
                    metrics={"resource": resource, "utilization": utilization},
                    recommendations=[
                        f"Monitor {resource} usage closely",
                        "Consider scaling up infrastructure",
                        "Implement resource optimization"
                    ]
                )
                alerts.append(alert)
        
        return alerts
    
    async def _check_campaign_completion(self, metrics: PipelineMetrics) -> List[Alert]:
        """Check campaign completion status and generate alerts."""
        
        alerts = []
        
        # Check for campaigns with insufficient variants
        # This would typically come from campaign-specific data
        # For now, we'll simulate this check
        
        return alerts
    
    async def _generate_ai_insights(
        self,
        metrics: PipelineMetrics,
        existing_alerts: List[Alert]
    ) -> List[Alert]:
        """Generate AI-powered insights and additional alerts."""
        
        try:
            # Prepare context for AI analysis
            context = {
                "current_metrics": {
                    "success_rate": metrics.success_rate,
                    "generation_time": metrics.average_generation_time,
                    "quality_score": metrics.quality_score_average,
                    "api_failures": metrics.api_failures,
                    "queue_depth": metrics.queue_depth
                },
                "recent_trends": self._analyze_trends(),
                "existing_alerts": [alert.alert_type for alert in existing_alerts]
            }
            
            # Generate AI insights
            insights_prompt = f"""
            Analyze the following creative automation pipeline metrics and provide insights:
            
            Current Metrics: {json.dumps(context['current_metrics'], indent=2)}
            Recent Trends: {json.dumps(context['recent_trends'], indent=2)}
            Existing Alerts: {context['existing_alerts']}
            
            Identify any patterns, anomalies, or potential issues that might not be caught by simple thresholds.
            Focus on:
            1. Performance trends and degradation patterns
            2. Quality issues that might affect brand compliance
            3. Resource bottlenecks or scaling needs
            4. User experience impacts
            
            Provide specific, actionable insights in JSON format with alert_type, level, and recommendations.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in creative automation and system monitoring. Provide technical insights and recommendations."
                    },
                    {
                        "role": "user",
                        "content": insights_prompt
                    }
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            # Parse AI response and create alerts
            # This is a simplified implementation - in reality, you'd parse the JSON response
            return []
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return []
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends from recent metrics."""
        
        if len(self.metrics_history) < 5:
            return {"insufficient_data": True}
        
        recent_metrics = self.metrics_history[-5:]
        
        trends = {
            "success_rate_trend": self._calculate_trend([m.success_rate for m in recent_metrics]),
            "generation_time_trend": self._calculate_trend([m.average_generation_time for m in recent_metrics]),
            "quality_score_trend": self._calculate_trend([m.quality_score_average for m in recent_metrics])
        }
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half > first_half * 1.05:
            return "increasing"
        elif second_half < first_half * 0.95:
            return "decreasing"
        else:
            return "stable"
    
    def _prepare_communication_context(self, alert: Alert, context: Dict[str, Any]) -> str:
        """Prepare context for AI communication generation."""
        
        return f"""
        Generate a stakeholder communication for the following alert:
        
        Alert Type: {alert.alert_type}
        Level: {alert.level}
        Title: {alert.title}
        Description: {alert.description}
        Timestamp: {alert.timestamp}
        Campaign ID: {alert.campaign_id or 'N/A'}
        
        Additional Context: {json.dumps(context, indent=2)}
        
        Recommendations: {alert.recommendations or []}
        
        Generate a clear, professional communication that explains:
        1. What happened (in business terms)
        2. Why it happened (root cause)
        3. What we're doing about it (immediate actions)
        4. How we'll prevent it (long-term solutions)
        5. Expected timeline for resolution
        """
    
    def _generate_fallback_communication(self, alert: Alert, context: Dict[str, Any]) -> str:
        """Generate fallback communication when AI is unavailable."""
        
        return f"""
        ALERT: {alert.title}
        
        Description: {alert.description}
        
        Impact: This issue may affect campaign delivery timelines and creative quality.
        
        Actions Taken:
        - Issue has been identified and logged
        - Technical team has been notified
        - Monitoring systems are tracking resolution
        
        Next Steps:
        {chr(10).join(f"- {rec}" for rec in (alert.recommendations or []))}
        
        Expected Resolution: Within 2-4 hours
        
        For questions or updates, please contact the technical team.
        """
    
    def _generate_fallback_delay_email(
        self,
        campaign_id: str,
        delay_reason: str,
        estimated_resolution: str
    ) -> str:
        """Generate fallback delay email when AI is unavailable."""
        
        return f"""
        Subject: Campaign Delay Notification - {campaign_id}
        
        Dear Leadership Team,
        
        I am writing to inform you of a delay in the processing of campaign {campaign_id}.
        
        Delay Reason: {delay_reason}
        
        Our technical team is actively working to resolve this issue. We expect to have the campaign back on track by {estimated_resolution}.
        
        We apologize for any inconvenience this may cause and appreciate your patience as we work to ensure the highest quality output for your campaign.
        
        We will provide updates as we progress and will notify you immediately once the issue is resolved.
        
        Best regards,
        Creative Automation Team
        """
