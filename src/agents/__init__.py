"""
AI-Driven Agents for Creative Automation Pipeline

This module contains intelligent agents that monitor the pipeline,
generate alerts, and communicate with stakeholders.
"""

from .monitoring_agent import MonitoringAgent, Alert, AlertLevel, AlertType, PipelineMetrics
from .communication_templates import (
    CommunicationTemplates, CommunicationContext, 
    StakeholderType, CommunicationType
)

__all__ = [
    "MonitoringAgent",
    "Alert",
    "AlertLevel", 
    "AlertType",
    "PipelineMetrics",
    "CommunicationTemplates",
    "CommunicationContext",
    "StakeholderType",
    "CommunicationType"
]

