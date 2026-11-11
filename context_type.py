from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class MemoryContext(BaseModel):
    user_id: str = "local-user"
    org_id: str = "default-org"
