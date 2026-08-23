"""Add authoritative source fields and disassembly steps."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260823_0003"
down_revision: str | None = "20260823_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("parts") as batch:
        batch.add_column(sa.Column("official_name", sa.String(160)))
        batch.add_column(sa.Column("source_url", sa.Text()))
        batch.add_column(
            sa.Column("verification_status", sa.String(40), nullable=False, server_default="unverified")
        )
    op.create_table(
        "disassembly_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("target_part_id", sa.Integer(), sa.ForeignKey("parts.id")),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("tool", sa.String(200)),
        sa.Column("safety_notice", sa.Text()),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("verification_status", sa.String(40), nullable=False, server_default="official"),
        sa.UniqueConstraint("product_id", "step_order"),
    )
    op.create_index("ix_disassembly_steps_product_id", "disassembly_steps", ["product_id"])


def downgrade() -> None:
    op.drop_table("disassembly_steps")
    with op.batch_alter_table("parts") as batch:
        batch.drop_column("verification_status")
        batch.drop_column("source_url")
        batch.drop_column("official_name")
