"""add pot table

Revision ID: 1c96749239ec
Revises: 4501ccd65d74
Create Date: 2026-08-29 21:57:00.362796

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1c96749239ec"
down_revision = "4501ccd65d74"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pot",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("monthly_amount", sa.Float(), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=False),
        sa.Column("note", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pot_user_id", "pot", ["user_id"])


def downgrade():
    op.drop_index("ix_pot_user_id", table_name="pot")
    op.drop_table("pot")
