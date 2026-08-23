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
    exploded_transform: dict = Field(
        default_factory=lambda: {
            "position": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
        }
    )
    explosion_axis: str = Field(default="z", pattern=r"^[xyz]$|^-[xyz]$")
    explosion_level: int = Field(default=0, ge=0)
    display_group: str | None = Field(default=None, max_length=80)
    is_detachable: bool = True
    official_name: str | None = Field(default=None, max_length=160)
    source_url: str | None = None
    verification_status: str = Field(default="unverified", max_length=40)
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
    exploded_transform: dict | None = None
    explosion_axis: str | None = Field(default=None, pattern=r"^[xyz]$|^-[xyz]$")
    explosion_level: int | None = Field(default=None, ge=0)
    display_group: str | None = Field(default=None, max_length=80)
    is_detachable: bool | None = None
    official_name: str | None = Field(default=None, max_length=160)
    source_url: str | None = None
    verification_status: str | None = Field(default=None, max_length=40)
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
    exploded_transform: dict
    explosion_axis: str
    explosion_level: int
    display_group: str | None
    is_detachable: bool
    official_name: str | None
    source_url: str | None
    verification_status: str
    sort_order: int


class ConnectionCreate(BaseModel):
    source_part_id: int
    target_part_id: int
    connection_type: str = Field(default="attach", max_length=80)
    instruction: str | None = None
    step_order: int = 0
    snap_tolerance: float = Field(default=0.08, gt=0, le=1)


class ConnectionRead(ORMModel):
    id: int
    product_id: int
    source_part_id: int
    target_part_id: int
    connection_type: str
    instruction: str | None
    step_order: int
    snap_tolerance: float


class DisassemblyStepCreate(BaseModel):
    target_part_id: int | None = None
    step_order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=160)
    instruction: str = Field(min_length=1)
    tool: str | None = Field(default=None, max_length=200)
    safety_notice: str | None = None
    source_url: str
    verification_status: str = Field(default="official", max_length=40)


class DisassemblyStepRead(ORMModel):
    id: int
    product_id: int
    target_part_id: int | None
    step_order: int
    title: str
    instruction: str
    tool: str | None
    safety_notice: str | None
    source_url: str
    verification_status: str


class ProductDetail(ProductRead):
    category: CategoryRead
    parts: list[PartRead]
    connections: list[ConnectionRead]
    disassembly_steps: list[DisassemblyStepRead]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AssetRead(BaseModel):
    filename: str
    url: str
    content_type: str
    size: int
