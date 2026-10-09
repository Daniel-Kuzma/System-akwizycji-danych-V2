from pydantic import BaseModel, Field

class CultivationRequest(BaseModel):
    name_of_cultivation : str = Field(min_length = 3, max_length = 100)
    min_temperature : float = Field(lt = 50.0, gt = -25.0)
    max_temperature : float = Field(lt = 50.0, gt = -25.0)
    min_humidity : float = Field(lt = 100.0, gt = 0.0)
    max_humidity : float = Field(lt = 100.0, gt = 0.0)
