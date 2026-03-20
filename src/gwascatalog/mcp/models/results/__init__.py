"""
Result models returned by MCP tool functions.

These models represent the structured data returned to agents by each tool,
collapsed from raw API response structures and optimised for token efficiency.
"""

from gwascatalog.mcp.models.results.ancestry import AncestryResult
from gwascatalog.mcp.models.results.associations import AssociationResult
from gwascatalog.mcp.models.results.pagination import PageSummary
from gwascatalog.mcp.models.results.studies import StudyResult
from gwascatalog.mcp.models.results.tool_response import ToolResponse
from gwascatalog.mcp.models.results.traits import TraitResult

__all__ = [
    "AncestryResult",
    "AssociationResult",
    "PageSummary",
    "StudyResult",
    "ToolResponse",
    "TraitResult",
]
