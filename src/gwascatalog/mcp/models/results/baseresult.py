from pydantic import BaseModel, ConfigDict


class BaseResult(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)
