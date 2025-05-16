"""add descricao to categoria_listas

Revision ID: add_descricao_to_categoria_listas
Revises: 
Create Date: 2025-05-16 10:02:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_descricao_to_categoria_listas'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add descricao column to categoria_listas table
    op.add_column('categoria_listas', sa.Column('descricao', sa.Text(), nullable=True), schema='gepes')


def downgrade():
    # Remove descricao column from categoria_listas table
    op.drop_column('categoria_listas', 'descricao', schema='gepes')
