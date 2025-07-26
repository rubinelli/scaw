"""Add tension tracking system

Revision ID: add_tension_tracking_system
Revises: 329babde56d8
Create Date: 2025-01-26 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_tension_tracking_system'
down_revision: Union[str, Sequence[str], None] = '329babde56d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tension_event table
    op.create_table('tension_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_data', sa.JSON(), nullable=True),
        sa.Column('severity_level', sa.Integer(), nullable=True),
        sa.Column('max_severity', sa.Integer(), nullable=True),
        sa.Column('deadline_watches', sa.Integer(), nullable=False),
        sa.Column('watches_remaining', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('resolution_method', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('origin_map_point_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['origin_map_point_id'], ['map_point.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create resolution_condition table
    op.create_table('resolution_condition',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tension_event_id', sa.Integer(), nullable=False),
        sa.Column('condition_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('target_data', sa.JSON(), nullable=False),
        sa.Column('is_met', sa.Boolean(), nullable=True),
        sa.Column('met_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tension_event_id'], ['tension_event.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('resolution_condition')
    op.drop_table('tension_event')
