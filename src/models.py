from typing import List, Union

from pydantic import BaseModel


class Location(BaseModel):
    barcodes: Union[str, List[str]]
    names: List[str]
