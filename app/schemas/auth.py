from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="Логин пользователя")
    password: str = Field(..., min_length=1, max_length=256, description="Пароль пользователя")


class LoginResponse(BaseModel):
    status: str = Field(..., description="Результат аутентификации")
    user_id: str = Field(..., description="Идентификатор пользователя")
    username: str = Field(..., description="Логин пользователя")
    message: str = Field(..., description="Служебное сообщение")
