from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any
import uuid

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,   # 允許從ORM物件轉換
        populate_by_name=True,  # 允許別名映射
    )