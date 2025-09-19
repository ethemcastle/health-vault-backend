# core/signals.py
from typing import Any, Mapping, Optional
from django.dispatch import Signal

# Generic audit signal. Listeners should be robust to missing args.
audit_event: Signal = Signal()  # providing_args is deprecated
# Expected kwargs:
# - actor: Optional[User]
# - action: str  (e.g., "CREATE", "UPDATE", "DELETE", "READ")
# - target_type: str (e.g., "analyses.Analysis")
# - target_id: str
# - ip_address: Optional[str]
# - metadata: Optional[Mapping[str, Any]]
