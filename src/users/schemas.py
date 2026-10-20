from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ChangeInformationRequest(BaseModel):
    name : str 
    lastname : str 
    username : str 
    email : str 

class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(regex_engine="python-re")

    old_password : str = Field(description = "Provide your password")
    new_password : str = Field(min_length = 12, pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",
                           description = "The password should be 12 characters long and contain uppercase and lowercase letters and numbers")

class PasswordRequest(BaseModel):
    password : str = Field(description = "Provide your password")

class SuccessfulRespond(BaseModel):
    message : str

class UserInformationRespond(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name : str
    lastname : str
    username : str
    email : str
    created_at : datetime