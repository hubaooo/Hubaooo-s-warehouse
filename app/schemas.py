from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)
    description: str | None = None


class CategoryRead(ORMModel):
    id: int
    name: str
    slug: str
    description: str | None


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    brand: str | None = None
    summary: str | None = None
    cover_image_url: str | None = None
    model_3d_url: str | None = None
    is_published: bool = False


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    slug: str | None = Field(
        default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160
    )
    brand: str | None = None
    summary: str | None = None
    cover_image_url: str | None = None
    model_3d_url: str | None = None
    is_published: bool | None = None


class ProductRead(ORMModel):
    id: int
    category_id: int
    name: str
    slug: str
    brand: str | None
    summary: str | None
    cover_image_url: str | None
    model_3d_url: str | None
    is_published: bool
    created_at: datetime


class PartCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160)
    description: str | None = None
    working_principle: str | None = None
    material: str | None = None
    model_3d_url: str | None = None
    image_url: str | None = None
    transform: dict = Field(
        default_factory=lambda: {
            "position": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
        }
    )
    sort_order: int = 0


class PartUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    slug: str | None = Field(
        default=None, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=160
    )
    description: str | None = None
    working_principle: str | None = None
    material: str | None = None
    model_3d_url: str | None = None
    image_url: str | None = None
    transform: dict | None = None
    sort_order: int | None = None


class PartRead(ORMModel):
    id: int
    product_id: int
    name: str
    slug: str
    description: str | None
    working_principle: str | None
    material: str | None
    model_3d_url: str | None
    image_url: str | None
    transform: dict
    sort_order: int


class ConnectionCreate(BaseModel):
    source_part_id: int
    target_part_id: int
    connection_type: str = Field(default="attach", max_length=80)
    instruction: str | None = None
    step_order: int = 0


class ConnectionRead(ORMModel):
    id: int
    product_id: int
    source_part_id: int
    target_part_id: int
    connection_type: str
    instruction: str | None
    step_order: int


class ProductDetail(ProductRead):
    category: CategoryRead
    parts: list[PartRead]
    connections: list[ConnectionRead]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AssetRead(BaseModel):
    filename: str
    url: str
    content_type: str
    size: int
