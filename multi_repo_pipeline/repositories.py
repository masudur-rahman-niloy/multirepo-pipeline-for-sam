from pydantic import BaseModel
from typing import List

class RepositoryModel(BaseModel):
    name: str
    description: str = ''

repositories: List[RepositoryModel] = [
    RepositoryModel(
        name='repo1',
        description='repo1 description'
    ),
    RepositoryModel(
        name='repo2',
        description='repo2 description'
    )
]
