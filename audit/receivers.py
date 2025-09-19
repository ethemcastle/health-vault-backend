# audit/receivers.py
from typing import Any, Mapping, Optional
from django.dispatch import receiver
from core.signals import audit_event
from audit.models import AuditLog

@receiver(audit_event)
def handle_audit_event(
    sender: Any,
    actor: Optional[Any] = None,
    action: str = "",
    target_type: str = "",
    target_id: str = "",
    ip_address: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> None:
    try:
        AuditLog.objects.create(
            actor=actor,
            action=action or AuditLog.Action.READ,
            target_type=target_type or (getattr(sender, "__name__", "") or "Unknown"),
            target_id=str(target_id or ""),
            ip_address=ip_address,
            metadata=dict(metadata or {}),
        )
    except Exception:
        # Never break the main request because of audit failures
        pass
