"""price_field

Revision ID: 91d5ff360882
Revises: cff396bf0072
Create Date: 2024-02-05 14:38:47.847344

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91d5ff360882'
down_revision = 'cff396bf0072'
branch_labels = None
depends_on = None

# тут работает создание create_foreign_key и удаление, проверил
def upgrade() -> None:
    with op.batch_alter_table('clients') as batch_op:
        batch_op.create_foreign_key('clients_duplicate_for', 'clients', ['duplicate_for'], ['id'])
    op.add_column('goods', sa.Column('price', sa.Numeric(), nullable=True))
    op.add_column('goods', sa.Column('url', sa.Text(), nullable=True))
    op.add_column('goods', sa.Column('image', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column('goods', 'image')
    op.drop_column('goods', 'url')
    op.drop_column('goods', 'price')
    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_constraint('clients_duplicate_for', type_='foreignkey')
    # ### end Alembic commands ###
