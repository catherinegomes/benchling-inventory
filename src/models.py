from typing import List, Union
from pydantic import BaseModel


class Location():
    barcodes: Union[str, List[str]]
    names: List[str]