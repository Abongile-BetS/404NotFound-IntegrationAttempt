from pydantic import BaseModel, Field


class UserResponse(BaseModel):
	id: str | None = None
	username: str | None = None
	email: str | None = None
	roles: list[str] = Field(default_factory=list)
