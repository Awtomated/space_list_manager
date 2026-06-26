"""
Intentionally minimal. RBAC is the host project's responsibility.
The host project should override get_queryset() and destroy() on the
viewsets to enforce its own access rules.
"""
