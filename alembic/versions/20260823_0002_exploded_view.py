"""Add exploded-view layout and assembly tolerance."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260823_0002"
down_revision: str | None = "20260823_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_TRANSFORM = '{"position":[0,0,0],"rotation":[0,0,0],"scale":[1,1,1]}'


def upgrade() -> None:
    with op.batch_alter_table("parts") as batch:
        batch.add_column(
            sa.Column(
                "exploded_transform", sa.JSON(), nullable=False, server_default=DEFAULT_TRANSFORM
            )
        )
        batch.add_column(sa.Column("explosion_axis", sa.String(10), nullable=False, server_default="z"))
        batch.add_column(sa.Column("explosion_level", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("display_group", sa.String(80)))
        batch.add_column(sa.Column("is_detachable", sa.Boolean(), nullable=False, server_default=sa.true()))
    with op.batch_alter_table("assembly_connections") as batch:
        batch.add_column(sa.Column("snap_tolerance", sa.Float(), nullable=False, server_default="0.08"))


def downgrade() -> None:
    with op.batch_alter_table("assembly_connections") as batch:
        batch.drop_column("snap_tolerance")
    with op.batch_alter_table("parts") as batch:
        batch.drop_column("is_detachable")
        batch.drop_column("display_group")
        batch.drop_column("explosion_level")
        batch.drop_column("explosion_axis")
        batch.drop_column("exploded_transform")
