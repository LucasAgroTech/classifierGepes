"""alter valor column to text

Revision ID: alter_valor_column_to_text
Revises: add_descricao_to_categoria_listas
Create Date: 2025-05-16 10:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'alter_valor_column_to_text'
down_revision = 'add_descricao_to_categoria_listas'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar o tipo da coluna valor para TEXT
    op.alter_column('categoria_listas', 'valor', 
                    existing_type=sa.VARCHAR(length=255),
                    type_=sa.Text(),
                    existing_nullable=False,
                    schema='gepes')


def downgrade():
    # Reverter o tipo da coluna valor para VARCHAR(255)
    op.alter_column('categoria_listas', 'valor', 
                    existing_type=sa.Text(),
                    type_=sa.VARCHAR(length=255),
                    existing_nullable=False,
                    schema='gepes')
