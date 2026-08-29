"""add subscription.anchor_date

Revision ID: e689458708be
Revises: 53198b71b10f
Create Date: 2026-08-29 21:40:30.621413

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e689458708be"
down_revision = "53198b71b10f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("subscription", sa.Column("anchor_date", sa.Date(), nullable=True))


def downgrade():
    op.drop_column("subscription", "anchor_date")
