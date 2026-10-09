from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token : str
    token_type : str 

class CreateUserRequest(BaseModel):
    name : str = Field(min_length = 3)
    lastname : str 
    username : str = Field(min_length = 4)
    password : str = Field(min_length = 12, pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$",
                           description = "The password should be 12 characters long and contain uppercase and lowercase letters and numbers")
    email : str = Field(pattern = r"^.{1,}@[a-zA-Z]{1,}\.[a-zA-z]{2,}$")