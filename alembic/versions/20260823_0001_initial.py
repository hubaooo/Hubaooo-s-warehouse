"""Initial product teardown schema."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260823_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_admins_username", "admins", ["username"], unique=True)
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("description", sa.Text()),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=True)
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(160), nullable=False),
        sa.Column("brand", sa.String(120)),
        sa.Column("summary", sa.Text()),
        sa.Column("cover_image_url", sa.Text()),
        sa.Column("model_3d_url", sa.Text()),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_table(
        "parts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(160), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("working_principle", sa.Text()),
        sa.Column("material", sa.String(160)),
        sa.Column("model_3d_url", sa.Text()),
        sa.Column("image_url", sa.Text()),
        sa.Column("transform", sa.JSON(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("product_id", "slug"),
    )
    op.create_index("ix_parts_product_id", "parts", ["product_id"])
    op.create_table(
        "assembly_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("source_part_id", sa.Integer(), sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("target_part_id", sa.Integer(), sa.ForeignKey("parts.id"), nullable=False),
        sa.Column("connection_type", sa.String(80), nullable=False),
        sa.Column("instruction", sa.Text()),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("product_id", "source_part_id", "target_part_id"),
    )
    op.create_index("ix_assembly_connections_product_id", "assembly_connections", ["product_id"])


def downgrade() -> None:
    op.drop_table("assembly_connections")
    op.drop_table("parts")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("admins")
