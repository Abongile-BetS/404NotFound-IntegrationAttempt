from typing import Annotated

from fastapi import Query

PageLimit = Annotated[int, Query(ge=1, le=500)]
PageOffset = Annotated[int, Query(ge=0)]
