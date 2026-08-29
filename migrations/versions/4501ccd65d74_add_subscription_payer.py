"""add subscription.payer

Revision ID: 4501ccd65d74
Revises: e689458708be
Create Date: 2026-08-29 21:48:58.557836

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4501ccd65d74"
down_revision = "e689458708be"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "subscription",
        sa.Column(
            "payer",
            sa.String(length=20),
            nullable=False,
            server_default="shared",
        ),
    )


def downgrade():
    op.drop_column("subscription", "payer")
