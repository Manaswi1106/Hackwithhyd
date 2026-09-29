from typing import Any, Dict, List
from datetime import datetime

class ChangeDetector:
    """Detects and categorizes changes between market states."""
    
    @staticmethod
    def detect_changes(previous: Dict[str, Any], current: Dict[str, Any]) -> List[Dict[str, Any]]:
        changes = []
        
        # Numeric field comparisons
        numeric_fields = {
            'competitor_count': 'Competitors',
            'average_price': 'Average Price',
            'demand_index': 'Demand Signal',
            'customer_concentration': 'Customer Concentration',
            'cac_estimate': 'CAC Estimate',
        }
        
        for field, label in numeric_fields.items():
            prev = previous.get(field)
            curr = current.get(field)
            if prev is not None and curr is not None:
                if prev != curr:
                    pct_change = ((curr - prev) / max(abs(prev), 1)) * 100
                    changes.append({
                        'field': label,
                        'previous_value': prev,
                        'current_value': curr,
                        'change_type': 'increase' if curr > prev else 'decrease',
                        'percentage_change': round(pct_change, 1),
                        'significance': ChangeDetector._assess_significance(pct_change),
                        'timestamp': datetime.utcnow().isoformat(),
                    })
        
        # List field comparisons (locations, competitors)
        list_fields = {
            'locations': 'Location',
            'top_locations': 'Location',
            'competitor_names': 'Competitor',
        }
        
        handled_labels = set()
        for field, label in list_fields.items():
            if label in handled_labels:
                continue
            prev_items = previous.get(field) or previous.get('locations') or previous.get('top_locations') or []
            curr_items = current.get(field) or current.get('locations') or current.get('top_locations') or []
            prev_set = set(prev_items)
            curr_set = set(curr_items)
            if prev_set or curr_set:
                handled_labels.add(label)
            
            for item in curr_set - prev_set:
                changes.append({
                    'field': f'New {label}',
                    'previous_value': 'Not present',
                    'current_value': item,
                    'change_type': 'new',
                    'significance': 'medium',
                    'timestamp': datetime.utcnow().isoformat(),
                })
            
            for item in prev_set - curr_set:
                changes.append({
                    'field': f'Removed {label}',
                    'previous_value': item,
                    'current_value': 'No longer tracked',
                    'change_type': 'removed',
                    'significance': 'low',
                    'timestamp': datetime.utcnow().isoformat(),
                })
        
        return changes
    
    @staticmethod
    def _assess_significance(pct_change: float) -> str:
        abs_change = abs(pct_change)
        if abs_change > 20:
            return 'high'
        elif abs_change > 10:
            return 'medium'
        return 'low'
