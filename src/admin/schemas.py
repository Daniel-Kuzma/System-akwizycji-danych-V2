from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from uuid import UUID
from datetime import datetime

class RoleEnum(Enum):
    ADMIN = "admin"
    USER = "user"

class CultivationRequest(BaseModel):
    name_of_cultivation : str = Field(min_length = 3, max_length = 100, description = "Provide the name of the crop.")
    min_temperature : float = Field(lt = 51.0, gt = -26.0, description = "Specify the minimum temperature for cultivation.")
    max_temperature : float = Field(lt = 51.0, gt = -26.0, description = "Specify the maximum temperature for cultivation.")
    min_humidity : float = Field(lt = 101.0, gt = 0.0, description = "Specify the minimum humidity for cultivation.")
    max_humidity : float = Field(lt = 101.0, gt = 0.0, description = "Specify the maximum humidity for cultivation.")

class RoleRequest(BaseModel):
    model_config = ConfigDict(use_enum_values = True)
    role : RoleEnum = Field(description = "Choose new role for user: admin or suer.")

class AudiLogResponse(BaseModel):
    public_id : UUID
    action : str
    entity_type : str
    entity_id : str
    created_at : datetime

class AllDeviceResponse(BaseModel):
    public_id : UUID = Field(serialization_alias = "device_public_id")
    owner_public_id : UUID 
    name_of_cultivation : str
    device_name : str
    device_location : str

class DeviceInformationResponse(BaseModel):
    owner_public_id : UUID
    name_of_cultivation : str
    device_name : str
    device_location : str

class TelemetryDataResponse(BaseModel):
    device_public_id : UUID
    temperature_reading : float
    humidity_reading : float
    created_at : datetime

class DeviceApiKeyResponse(BaseModel):
    device_public_id : UUID
    token : str = Field(serialization_alias = "hashed_token")
    is_active : bool
    created_at : datetime

class NewDeviceInformationRequest(BaseModel):
    model_config = ConfigDict(use_enum_values = True)
    type_of_cultivation_id : int
    device_name : str
    device_location : str  
    is_email_alert_enable : bool