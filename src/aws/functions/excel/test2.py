from pydantic import BaseModel
from typing import Optional
from typing_extensions import TypedDict

from dashboard.backend.excel.objects import EntityDetails

class User(TypedDict):
    id: int
    name: str
    email: str
    other: int
    
# Function to get property names of a Pydantic model
def get_property_names(model: BaseModel) -> list:
    return list(model.__fields__.keys())

user_data = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
}
user = User(**user_data)

# property_names = get_property_names(User)

print(user["name"])

# print(property_names)