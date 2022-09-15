from datetime import date
from typing import Optional

from pydantic import BaseModel


class ItemSchemas(BaseModel):

    photo: Optional[str]
    title: str
    location: str
    date_posted: date
    beds: str
    description: str
    price: str