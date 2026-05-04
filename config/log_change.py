"""
Utility for logging user actions and changes.
"""

import logging
from django.utils import timezone
from apps.account.models import CustomUser

logger = logging.getLogger(__name__)


def log_change(user, ip, object_name, object_id, action_type, data=None):
    """
    Log user actions for audit trail.
    
    Args:
        user: User object who performed the action
        ip: IP address of the request
        object_name: Name of the object being acted upon
        object_id: ID of the object
        action_type: Type of action (create, update, delete, login, logout, etc.)
        data: Additional data about the action
    """
    try:
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user else None,
            'user_email': user.email if user else None,
            'ip_address': ip,
            'object_name': object_name,
            'object_id': object_id,
            'action_type': action_type,
            'data': data or {}
        }
        
        logger.info(f"User Action: {log_data}")
        
    except Exception as e:
        logger.error(f"Failed to log change: {str(e)}")
