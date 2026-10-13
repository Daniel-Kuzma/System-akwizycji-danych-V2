from pydantic import BaseModel, Field

class DeviceRequest(BaseModel):
    type_of_cultivation : int = Field(description = "Choose typ of cultivation")
    device_name : str = Field(description = "Provide name for your device", default = "Thermometer")
    device_location : str = Field(description = "Provide location for your device", default = "Greenhouse")

class ChangeDeviceInformationRequest(BaseModel):
    type_of_cultivation : int = Field(description = "Choose typ of cultivation")
    device_name : str = Field(description = "Provide name for your device")
    device_location : str = Field(description = "Provide location for your device")

class DeviceNameRequest(BaseModel):
    device_name : str = Field(description = "Provide device name to confirm delete")

