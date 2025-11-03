from pydantic import BaseModel, Field, SecretStr, constr, field_validator
from typing import Annotated

class Creds(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50, strip_whitespace=True)]
    password: SecretStr = Field(..., repr=False)  

    @field_validator("password")
    def password_min_len(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 3:
            raise ValueError("password must be at least 8 chars")
        return v
