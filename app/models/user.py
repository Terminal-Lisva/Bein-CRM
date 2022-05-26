from typing import TypedDict, Dict, Union


class DataDict(TypedDict):
    id: int
    last_name: str
    first_name: str
    patrotymic: str
    company: Dict[str, Union[int, str]]
