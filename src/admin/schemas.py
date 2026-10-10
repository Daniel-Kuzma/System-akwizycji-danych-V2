from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class RoleEnum(Enum):
    ADMIN = "admin"
    USER = "user"

class CultivationRequest(BaseModel):
    name_of_cultivation : str = Field(min_length = 3, max_length = 100, description = "Provide the name of the crop.")
    min_temperature : float = Field(lt = 50.0, gt = -25.0, description = "Specify the minimum temperature for cultivation.")
    max_temperature : float = Field(lt = 50.0, gt = -25.0, description = "Specify the maximum temperature for cultivation.")
    min_humidity : float = Field(lt = 100.0, gt = 0.0, description = "Specify the minimum humidity for cultivation.")
    max_humidity : float = Field(lt = 100.0, gt = 0.0, description = "Specify the maximum humidity for cultivation.")

class RoleRequest(BaseModel):
    model_config = ConfigDict(use_enum_values = True)
    role : RoleEnum = Field(description = "Choose new role for user.")