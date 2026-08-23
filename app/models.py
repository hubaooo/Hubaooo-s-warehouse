from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(120))
    summary: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(Text)
    model_3d_url: Mapped[str | None] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped[Category] = relationship(back_populates="products")
    parts: Mapped[list["Part"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="Part.sort_order"
    )
    connections: Mapped[list["AssemblyConnection"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    disassembly_steps: Mapped[list["DisassemblyStep"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="DisassemblyStep.step_order"
    )


class Part(Base):
    __tablename__ = "parts"
    __table_args__ = (UniqueConstraint("product_id", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text)
    working_principle: Mapped[str | None] = mapped_column(Text)
    material: Mapped[str | None] = mapped_column(String(160))
    model_3d_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    transform: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
    )
    exploded_transform: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}
    )
    explosion_axis: Mapped[str] = mapped_column(String(10), default="z")
    explosion_level: Mapped[int] = mapped_column(default=0)
    display_group: Mapped[str | None] = mapped_column(String(80))
    is_detachable: Mapped[bool] = mapped_column(Boolean, default=True)
    official_name: Mapped[str | None] = mapped_column(String(160))
    source_url: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(40), default="unverified")
    sort_order: Mapped[int] = mapped_column(default=0)

    product: Mapped[Product] = relationship(back_populates="parts")


class AssemblyConnection(Base):
    __tablename__ = "assembly_connections"
    __table_args__ = (UniqueConstraint("product_id", "source_part_id", "target_part_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    source_part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"))
    target_part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"))
    connection_type: Mapped[str] = mapped_column(String(80), default="attach")
    instruction: Mapped[str | None] = mapped_column(Text)
    step_order: Mapped[int] = mapped_column(default=0)
    snap_tolerance: Mapped[float] = mapped_column(Float, default=0.08)

    product: Mapped[Product] = relationship(back_populates="connections")
    source_part: Mapped[Part] = relationship(foreign_keys=[source_part_id])
    target_part: Mapped[Part] = relationship(foreign_keys=[target_part_id])


class DisassemblyStep(Base):
    __tablename__ = "disassembly_steps"
    __table_args__ = (UniqueConstraint("product_id", "step_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    target_part_id: Mapped[int | None] = mapped_column(ForeignKey("parts.id"))
    step_order: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column(String(160))
    instruction: Mapped[str] = mapped_column(Text)
    tool: Mapped[str | None] = mapped_column(String(200))
    safety_notice: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(40), default="official")

    product: Mapped[Product] = relationship(back_populates="disassembly_steps")
    target_part: Mapped[Part | None] = relationship()
