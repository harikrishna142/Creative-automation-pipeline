"""
Stakeholder Communication Templates for Creative Automation Pipeline

This module contains templates and utilities for generating professional
communications to various stakeholders about pipeline status, issues, and updates.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class StakeholderType(str, Enum):
    """Types of stakeholders who receive communications."""
    EXECUTIVE_LEADERSHIP = "executive_leadership"
    CREATIVE_LEAD = "creative_lead"
    AD_OPERATIONS = "ad_operations"
    IT_TEAM = "it_team"
    LEGAL_COMPLIANCE = "legal_compliance"
    CLIENT = "client"


class CommunicationType(str, Enum):
    """Types of communications."""
    STATUS_UPDATE = "status_update"
    INCIDENT_REPORT = "incident_report"
    PERFORMANCE_REPORT = "performance_report"
    DELAY_NOTIFICATION = "delay_notification"
    RESOLUTION_UPDATE = "resolution_update"
    MONTHLY_SUMMARY = "monthly_summary"


@dataclass
class CommunicationContext:
    """Context for generating communications."""
    stakeholder_type: StakeholderType
    communication_type: CommunicationType
    campaign_id: Optional[str] = None
    severity_level: str = "medium"
    affected_campaigns: List[str] = None
    metrics: Dict[str, Any] = None
    timeline: Dict[str, str] = None
    business_impact: str = ""
    technical_details: Dict[str, Any] = None


class CommunicationTemplates:
    """
    Templates for generating stakeholder communications.
    """
    
    def __init__(self):
        """Initialize communication templates."""
        self.templates = self._initialize_templates()
    
    def generate_communication(self, context: CommunicationContext) -> str:
        """
        Generate a communication based on context.
        
        Args:
            context: Communication context
            
        Returns:
            Generated communication text
        """
        template_key = f"{context.stakeholder_type}_{context.communication_type}"
        
        if template_key in self.templates:
            template = self.templates[template_key]
            return self._fill_template(template, context)
        else:
            # Use generic template
            return self._generate_generic_communication(context)
    
    def generate_delay_notification_email(
        self,
        campaign_id: str,
        delay_reason: str,
        estimated_resolution: str,
        business_impact: str = "",
        alternative_solutions: List[str] = None
    ) -> str:
        """
        Generate a delay notification email for customer leadership.
        
        Args:
            campaign_id: Campaign experiencing delay
            delay_reason: Technical reason for delay
            estimated_resolution: Estimated time to resolution
            business_impact: Business impact description
            alternative_solutions: List of alternative solutions
            
        Returns:
            Formatted email content
        """
        subject = f"Campaign Delay Notification - {campaign_id}"
        
        # Map technical reasons to business-friendly explanations
        business_reason = self._translate_technical_reason(delay_reason)
        
        # Calculate business impact
        if not business_impact:
            business_impact = self._calculate_business_impact(delay_reason, estimated_resolution)
        
        email_body = f"""
Subject: {subject}

Dear Leadership Team,

I am writing to inform you of a delay in the processing of campaign {campaign_id}.

**Situation Summary:**
{business_reason}

**Business Impact:**
{business_impact}

**Resolution Timeline:**
Our technical team is actively working to resolve this issue. We expect to have the campaign back on track by {estimated_resolution}.

**Immediate Actions:**
• Technical team has been mobilized to address the root cause
• Alternative processing methods are being evaluated
• Quality assurance processes remain active to ensure output standards

**Prevention Measures:**
• Enhanced monitoring systems have been implemented
• Backup processing capabilities are being activated
• Regular health checks will prevent similar issues

**Alternative Solutions:**
{self._format_alternatives(alternative_solutions)}

We apologize for any inconvenience this may cause and appreciate your patience as we work to ensure the highest quality output for your campaign.

We will provide updates every 2 hours until resolution and will notify you immediately once the issue is resolved.

If you have any questions or concerns, please don't hesitate to contact me directly.

Best regards,
Creative Automation Team
Technical Lead: [Contact Information]
Customer Success Manager: [Contact Information]

---
This is an automated notification from the Creative Automation Pipeline monitoring system.
        """
        
        return email_body.strip()
    
    def generate_performance_report(
        self,
        metrics: Dict[str, Any],
        stakeholder_type: StakeholderType,
        time_period: str = "monthly"
    ) -> str:
        """
        Generate a performance report for stakeholders.
        
        Args:
            metrics: Performance metrics
            stakeholder_type: Type of stakeholder
            time_period: Time period for the report
            
        Returns:
            Formatted performance report
        """
        if stakeholder_type == StakeholderType.EXECUTIVE_LEADERSHIP:
            return self._generate_executive_performance_report(metrics, time_period)
        elif stakeholder_type == StakeholderType.CREATIVE_LEAD:
            return self._generate_creative_performance_report(metrics, time_period)
        else:
            return self._generate_technical_performance_report(metrics, time_period)
    
    def generate_incident_report(
        self,
        incident_details: Dict[str, Any],
        stakeholder_type: StakeholderType
    ) -> str:
        """
        Generate an incident report for stakeholders.
        
        Args:
            incident_details: Details about the incident
            stakeholder_type: Type of stakeholder
            
        Returns:
            Formatted incident report
        """
        if stakeholder_type == StakeholderType.EXECUTIVE_LEADERSHIP:
            return self._generate_executive_incident_report(incident_details)
        else:
            return self._generate_technical_incident_report(incident_details)
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize communication templates."""
        
        return {
            # Executive Leadership Templates
            "executive_leadership_status_update": """
**Creative Automation Pipeline Status Update**

**Overall Health:** {status}
**Campaigns Processed:** {total_campaigns}
**Success Rate:** {success_rate:.1%}
**Average Quality Score:** {avg_quality:.2f}

**Key Metrics:**
• Generation Time: {avg_generation_time:.1f}s
• API Reliability: {api_reliability:.1%}
• Resource Utilization: {resource_utilization:.1%}

**Recent Highlights:**
{highlights}

**Areas of Focus:**
{focus_areas}

**Next Steps:**
{next_steps}
            """,
            
            "executive_leadership_incident_report": """
**Incident Report - Creative Automation Pipeline**

**Incident Summary:**
{incident_summary}

**Business Impact:**
• Affected Campaigns: {affected_campaigns}
• Estimated Revenue Impact: {revenue_impact}
• Customer Impact: {customer_impact}

**Root Cause:**
{root_cause}

**Resolution:**
{resolution}

**Prevention Measures:**
{prevention_measures}

**Timeline:**
• Detection: {detection_time}
• Resolution: {resolution_time}
• Total Downtime: {downtime}
            """,
            
            # Creative Lead Templates
            "creative_lead_performance_report": """
**Creative Quality Performance Report**

**Quality Metrics:**
• Average Quality Score: {avg_quality:.2f}
• Brand Compliance Rate: {brand_compliance:.1%}
• Content Moderation Pass Rate: {content_moderation:.1%}

**Creative Output:**
• Total Creatives Generated: {total_creatives}
• Aspect Ratio Distribution: {aspect_ratios}
• Product Coverage: {product_coverage}

**Quality Issues:**
{quality_issues}

**Recommendations:**
{recommendations}
            """,
            
            # IT Team Templates
            "it_team_incident_report": """
**Technical Incident Report**

**System:** Creative Automation Pipeline
**Severity:** {severity}
**Duration:** {duration}

**Technical Details:**
• Error Codes: {error_codes}
• Affected Components: {affected_components}
• System Resources: {system_resources}

**Root Cause Analysis:**
{root_cause}

**Resolution Steps:**
{resolution_steps}

**Monitoring Updates:**
{monitoring_updates}

**Prevention Actions:**
{prevention_actions}
            """
        }
    
    def _fill_template(self, template: str, context: CommunicationContext) -> str:
        """Fill template with context data."""
        
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated template filling
        filled_template = template
        
        if context.metrics:
            for key, value in context.metrics.items():
                placeholder = f"{{{key}}}"
                filled_template = filled_template.replace(placeholder, str(value))
        
        return filled_template
    
    def _generate_generic_communication(self, context: CommunicationContext) -> str:
        """Generate a generic communication when no specific template exists."""
        
        return f"""
**{context.communication_type.replace('_', ' ').title()}**

**Stakeholder:** {context.stakeholder_type.replace('_', ' ').title()}
**Severity:** {context.severity_level}
**Timestamp:** {datetime.now().isoformat()}

**Details:**
{context.business_impact or 'No additional details provided.'}

**Technical Information:**
{context.technical_details or 'No technical details available.'}

**Timeline:**
{context.timeline or 'No timeline information available.'}
        """
    
    def _translate_technical_reason(self, technical_reason: str) -> str:
        """Translate technical reasons to business-friendly explanations."""
        
        translations = {
            "api_failure": "Temporary service interruption with our AI content generation partner",
            "quality_threshold_breach": "Content quality standards not met, requiring additional processing",
            "resource_exhaustion": "High demand causing temporary processing delays",
            "generation_delay": "Complex content requirements taking longer than expected",
            "missing_assets": "Additional creative assets needed to complete campaign requirements",
            "brand_compliance_issue": "Content review required to ensure brand guideline compliance"
        }
        
        return translations.get(technical_reason, f"Technical issue: {technical_reason}")
    
    def _calculate_business_impact(self, delay_reason: str, estimated_resolution: str) -> str:
        """Calculate business impact based on delay reason and resolution time."""
        
        impact_templates = {
            "api_failure": "Campaign launch may be delayed by 2-4 hours, affecting initial engagement metrics.",
            "quality_threshold_breach": "Content review and regeneration may delay launch by 1-2 hours.",
            "resource_exhaustion": "Processing delays may impact campaign timing by 1-3 hours.",
            "generation_delay": "Complex content requirements may extend delivery timeline by 2-6 hours.",
            "missing_assets": "Additional asset creation may delay campaign by 4-8 hours.",
            "brand_compliance_issue": "Content review and approval may delay launch by 1-4 hours."
        }
        
        return impact_templates.get(delay_reason, "Processing delay may impact campaign timeline.")
    
    def _format_alternatives(self, alternatives: Optional[List[str]]) -> str:
        """Format alternative solutions for email."""
        
        if not alternatives:
            return "• Manual review and approval of existing content\n• Expedited processing queue for priority campaigns"
        
        return "\n".join(f"• {alt}" for alt in alternatives)
    
    def _generate_executive_performance_report(self, metrics: Dict[str, Any], time_period: str) -> str:
        """Generate executive-level performance report."""
        
        return f"""
**Executive Performance Report - {time_period.title()}**

**Business Impact:**
• Campaigns Delivered: {metrics.get('total_campaigns', 0)}
• Revenue Generated: ${metrics.get('revenue_impact', 0):,.2f}
• Cost Savings: ${metrics.get('cost_savings', 0):,.2f}
• ROI: {metrics.get('roi', 0):.1%}

**Operational Excellence:**
• Success Rate: {metrics.get('success_rate', 0):.1%}
• Average Delivery Time: {metrics.get('avg_delivery_time', 0):.1f} hours
• Quality Score: {metrics.get('avg_quality', 0):.2f}
• Customer Satisfaction: {metrics.get('customer_satisfaction', 0):.1%}

**Strategic Initiatives:**
• Automation Coverage: {metrics.get('automation_coverage', 0):.1%}
• Process Efficiency: {metrics.get('process_efficiency', 0):.1%}
• Innovation Index: {metrics.get('innovation_index', 0):.2f}

**Key Achievements:**
{metrics.get('achievements', 'No specific achievements recorded.')}

**Areas for Improvement:**
{metrics.get('improvement_areas', 'Continue monitoring performance metrics.')}

**Next Quarter Focus:**
{metrics.get('next_quarter_focus', 'Maintain current performance levels and explore expansion opportunities.')}
        """
    
    def _generate_creative_performance_report(self, metrics: Dict[str, Any], time_period: str) -> str:
        """Generate creative team performance report."""
        
        return f"""
**Creative Performance Report - {time_period.title()}**

**Creative Output:**
• Total Creatives Generated: {metrics.get('total_creatives', 0)}
• Unique Campaigns: {metrics.get('unique_campaigns', 0)}
• Aspect Ratios Covered: {metrics.get('aspect_ratios', 0)}
• Products Featured: {metrics.get('products_featured', 0)}

**Quality Metrics:**
• Average Quality Score: {metrics.get('avg_quality', 0):.2f}
• Brand Compliance Rate: {metrics.get('brand_compliance', 0):.1%}
• Content Moderation Pass: {metrics.get('content_moderation', 0):.1%}
• A/B Test Performance: {metrics.get('ab_test_performance', 0):.1%}

**Creative Trends:**
• Most Popular Aspect Ratio: {metrics.get('popular_aspect_ratio', 'N/A')}
• Top Performing Product Category: {metrics.get('top_category', 'N/A')}
• Average Creative Complexity: {metrics.get('avg_complexity', 0):.2f}

**Quality Issues:**
{metrics.get('quality_issues', 'No significant quality issues identified.')}

**Recommendations:**
{metrics.get('recommendations', 'Continue current creative processes and quality standards.')}
        """
    
    def _generate_technical_performance_report(self, metrics: Dict[str, Any], time_period: str) -> str:
        """Generate technical performance report."""
        
        return f"""
**Technical Performance Report - {time_period.title()}**

**System Performance:**
• Uptime: {metrics.get('uptime', 0):.1%}
• Average Response Time: {metrics.get('avg_response_time', 0):.2f}s
• Throughput: {metrics.get('throughput', 0):.1f} campaigns/hour
• Error Rate: {metrics.get('error_rate', 0):.2%}

**Resource Utilization:**
• CPU Usage: {metrics.get('cpu_usage', 0):.1%}
• Memory Usage: {metrics.get('memory_usage', 0):.1%}
• Storage Usage: {metrics.get('storage_usage', 0):.1%}
• Network Usage: {metrics.get('network_usage', 0):.1%}

**API Performance:**
• AI Service Calls: {metrics.get('ai_calls', 0)}
• API Success Rate: {metrics.get('api_success_rate', 0):.1%}
• Average API Response: {metrics.get('avg_api_response', 0):.2f}s
• Rate Limit Hits: {metrics.get('rate_limit_hits', 0)}

**Incidents:**
• Total Incidents: {metrics.get('total_incidents', 0)}
• Critical Incidents: {metrics.get('critical_incidents', 0)}
• Mean Time to Resolution: {metrics.get('mttr', 0):.1f} hours
• Mean Time Between Failures: {metrics.get('mtbf', 0):.1f} hours

**Improvements:**
{metrics.get('improvements', 'No specific improvements recorded.')}
        """
    
    def _generate_executive_incident_report(self, incident_details: Dict[str, Any]) -> str:
        """Generate executive-level incident report."""
        
        return f"""
**Executive Incident Report**

**Incident Summary:**
{incident_details.get('summary', 'No summary provided')}

**Business Impact:**
• Affected Revenue: ${incident_details.get('revenue_impact', 0):,.2f}
• Customer Impact: {incident_details.get('customer_impact', 'Unknown')}
• Reputation Risk: {incident_details.get('reputation_risk', 'Low')}

**Timeline:**
• Detection: {incident_details.get('detection_time', 'Unknown')}
• Resolution: {incident_details.get('resolution_time', 'Unknown')}
• Total Impact Duration: {incident_details.get('duration', 'Unknown')}

**Root Cause:**
{incident_details.get('root_cause', 'Under investigation')}

**Immediate Actions:**
{incident_details.get('immediate_actions', 'Technical team mobilized')}

**Prevention Measures:**
{incident_details.get('prevention_measures', 'Enhanced monitoring implemented')}

**Lessons Learned:**
{incident_details.get('lessons_learned', 'Review in progress')}
        """
    
    def _generate_technical_incident_report(self, incident_details: Dict[str, Any]) -> str:
        """Generate technical incident report."""
        
        return f"""
**Technical Incident Report**

**System:** Creative Automation Pipeline
**Severity:** {incident_details.get('severity', 'Unknown')}
**Incident ID:** {incident_details.get('incident_id', 'N/A')}

**Technical Details:**
• Error Codes: {incident_details.get('error_codes', 'N/A')}
• Affected Components: {incident_details.get('affected_components', 'N/A')}
• System State: {incident_details.get('system_state', 'Unknown')}

**Timeline:**
• First Occurrence: {incident_details.get('first_occurrence', 'Unknown')}
• Detection: {incident_details.get('detection_time', 'Unknown')}
• Resolution: {incident_details.get('resolution_time', 'Unknown')}

**Root Cause Analysis:**
{incident_details.get('root_cause', 'Under investigation')}

**Resolution Steps:**
{incident_details.get('resolution_steps', 'Technical team working on resolution')}

**Monitoring Updates:**
{incident_details.get('monitoring_updates', 'Enhanced monitoring active')}

**Prevention Actions:**
{incident_details.get('prevention_actions', 'Review and update prevention measures')}
        """
