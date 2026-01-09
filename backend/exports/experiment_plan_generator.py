"""
Experiment Plan Generator

Generates markdown experiment plans for recommendations.
"""

from typing import Dict, Optional
from datetime import datetime


class ExperimentPlanGenerator:
    """Generates experiment plans"""
    
    def generate_plan(self, action: Dict,
                     incident_id: str,
                     incident_metric: str) -> str:
        """
        Generate experiment plan markdown
        
        Args:
            action: Action recommendation dict
            incident_id: Incident ID
            incident_metric: Metric that regressed
        
        Returns:
            Markdown string
        """
        action_name = action.get('name', 'Unknown Action')
        expected_cx_impact = action.get('expected_cx_impact', 0)
        expected_efficiency_impact = action.get('expected_efficiency_impact', 0)
        confidence = action.get('confidence', 0.5)
        
        markdown = f"""# Experiment Plan: {action_name}

## Hypothesis

{action.get('description', 'N/A')}

Implementing this action will improve {incident_metric} by approximately {expected_cx_impact:.1f} points, with an efficiency impact of {expected_efficiency_impact:+.1f}%.

## Primary Metrics

- **CX Score**: Target improvement of +{expected_cx_impact:.1f} points
- **{incident_metric.replace('_', ' ').title()}**: Target improvement based on action impact
- **On-time Rate**: Monitor for improvement
- **Cancellation Rate**: Monitor for reduction

## Secondary Metrics

- **Refund Rate**: Monitor for changes
- **Support Contact Rate**: Monitor for changes
- **Item Accuracy**: Monitor for changes
- **Rating Proxy**: Monitor for improvement

## Guardrails

- **Dasher Efficiency**: Alert if efficiency drops > 10%
- **Order Volume**: Alert if order volume drops > 5%
- **Other Regions**: Monitor for spillover effects
- **Customer Wait Time**: Alert if average wait time increases significantly

## Unit of Randomization

Store-level randomization (randomize 50% of affected stores)

## Duration & Sample Size

- **Minimum Duration**: 7 days
- **Recommended Duration**: 14 days
- **Expected Sample Size**: ~5,000 orders (treatment group)
- **Power**: 80% to detect 5% lift in primary metric

## Rollout Plan

### Phase 1: 10% stores (Day 1-3)
- Monitor closely for any adverse effects
- Validate metrics are tracking as expected

### Phase 2: 50% stores (Day 4-7)
- Continue monitoring
- Compare treatment vs control

### Phase 3: 100% stores (Day 8-14)
- Full rollout
- Final evaluation

## Monitoring Checklist

- [ ] Daily CX Score check (target: +{expected_cx_impact:.1f} points)
- [ ] Daily primary metric check
- [ ] Daily guardrail checks
- [ ] Hourly alerts if metrics regress
- [ ] Rollback plan ready if guardrails breached

## Rollback Criteria

- CX Score drops below baseline
- Guardrail metrics breach thresholds
- Significant adverse effects detected

## Confidence

Estimated confidence in impact: {confidence:.0%}

## Generated

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Incident ID: {incident_id}
"""
        
        return markdown

