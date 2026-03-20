from typing import Any

from pydantic import BaseModel, ConfigDict, model_serializer


def _strip_empty(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values and empty lists from a serialized result dict."""
    return {k: v for k, v in data.items() if v is not None and v != []}


class BaseResult(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    @model_serializer(mode="wrap")
    def _strip(self, handler: Any) -> dict[str, Any]:
        return _strip_empty(handler(self))
