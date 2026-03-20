from pydantic import BaseModel, ConfigDict

from gwascatalog.mcp.models.params.types import (
    PageField,
    SizeField,
    SortDirectionField,
)


class Params(BaseModel):
    """Base model for MCP tool parameters.

    All MCP tool parameter models should inherit from this base, which
    validates and sets defaults for common pagination and sorting parameters.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    page: PageField = 0
    size: SizeField = 10
    direction: SortDirectionField = "asc"

    def __hash__(self) -> int:
        """
        Stable hash based on the JSON representation of the model

        Useful for caching tool results based on parameters
        """
        return hash(self.model_dump_json(by_alias=True, exclude_none=False))
