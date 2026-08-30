"""add subscription.paid_from

Revision ID: b7d419e2c8a1
Revises: 1c96749239ec
Create Date: 2026-08-30 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b7d419e2c8a1"
down_revision = "1c96749239ec"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "subscription",
        sa.Column("paid_from", sa.String(length=1), nullable=True),
    )
    # Backfill: a bill owned by one person is assumed to leave that person's
    # account. Shared bills stay NULL until the user assigns an account.
    op.execute("UPDATE subscription SET paid_from = payer WHERE payer IN ('a', 'b')")


def downgrade():
    op.drop_column("subscription", "paid_from")
