from pydantic import BaseModel, Field

class ChangeInformationRequest(BaseModel):
    name : str 
    lastname : str 
    username : str 
    email : str 

class ChangePasswordRequest(BaseModel):
    old_password : str = Field(description = "Provide your password")
    new_password : str = Field(min_length = 12, pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",
                           description = "The password should be 12 characters long and contain uppercase and lowercase letters and numbers")

class PasswordRequest(BaseModel):
    password : str = Field(description = "Provide your password")