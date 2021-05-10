"""create main tables
Revision ID: 12345678654
Revises:
Create Date: 2020-05-05 10:41:35.468471
"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = "12345678654"
down_revision = None
branch_labels = None
depends_on = None


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )

def create_add_equity_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION insert_equity_into_securities()
            RETURNS TRIGGER AS
        $$
        BEGIN
            INSERT INTO securities (ticker, type)
            VALUES (NEW.ticker, 'equity');
            RETURN NULL;
        END;
        $$ language 'plpgsql';
        """
    )


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "added_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )

def create_securities_table() -> None:
    op.create_table(
        "securities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticker", sa.Text, nullable=False, index=True),
        sa.Column("type", sa.Text, nullable=False),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_securities_modtime
            BEFORE UPDATE
            ON securities
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )

def create_equities_table() -> None:
    op.create_table(
        "equities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticker", sa.Text, nullable=False, index=True),
        sa.Column("name", sa.Text, nullable=True),
        sa.Column("country", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("sector", sa.Text, nullable=True),
        sa.Column("industry", sa.Text, nullable=True),
        sa.Column("exchange", sa.Text, nullable=True),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_equities_modtime
            BEFORE UPDATE
            ON equities
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )
    op.execute(
        """
        CREATE TRIGGER insert_equities_into_securities
            AFTER INSERT
            ON equities
            FOR EACH ROW
        EXECUTE PROCEDURE insert_equity_into_securities();"""
    )

def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email", sa.Text, unique=True, nullable=False, index=True),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="False"),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="True"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="False"),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_updated_at_trigger()
    create_add_equity_trigger()
    create_securities_table()
    create_equities_table()
    create_users_table()


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table('securities')
    op.drop_table("equities")
    op.execute("DROP FUNCTION update_updated_at_column")
    op.execute("DROP FUNCTION insert_equity_into_securities()")