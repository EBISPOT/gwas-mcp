from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from gwascatalog.mcp.models.params.types import (
    Page,
    Size,
    SortDirection,
    SortDirectionField,
    SortKeyField,
)


class Params(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    page: Page = 0
    size: Size = 10
    sort: SortKeyField | None = None
    direction: SortDirectionField | None = None

    @model_validator(mode="after")
    def set_default_sort_direction(self) -> Self:
        """Ensure that direction defaults to ASC if sort is provided but no
        direction."""
        if self.sort is not None and self.direction is None:
            # model_copy because the model is immutable
            return self.model_copy(update={"direction": SortDirection.ASC})
        return self
