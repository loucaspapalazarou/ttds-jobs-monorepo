from pydantic import BaseModel, HttpUrl

from typing import Sequence
from bson import ObjectId
from typing import List,Optional
from pydantic import BaseModel, Field





class Job(BaseModel):
    id:int=Field(example=1)
    title:str=Field(example="")
    description:str=Field(example="")
    company:str=Field(example="")
    requirements:str=Field(example="")
    link:str=Field(example="")
    description:str=Field(example="")
    data:int=Field(example=1)
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: int}

