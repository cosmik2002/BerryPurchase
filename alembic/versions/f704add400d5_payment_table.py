"""payment table

Revision ID: f704add400d5
Revises: 5255fe063f94
Create Date: 2023-02-01 19:27:50.835562

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f704add400d5'
down_revision = '5255fe063f94'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('variants', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sms_id', sa.Integer(), nullable=True),
    sa.Column('payer_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('sum', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['payer_id'], ['payers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_payer_id'), 'payments', ['payer_id'], unique=False)
    op.create_index(op.f('ix_payments_sms_id'), 'payments', ['sms_id'], unique=False)
    op.create_index(op.f('ix_payments_timestamp'), 'payments', ['timestamp'], unique=False)
    op.add_column('payers', sa.Column('comments', sa.Text(), nullable=True))
    op.create_index(op.f('ix_payers_name'), 'payers', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payers_name'), table_name='payers')
    op.drop_column('payers', 'comments')
    op.drop_index(op.f('ix_payments_timestamp'), table_name='payments')
    op.drop_index(op.f('ix_payments_sms_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_payer_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_table('goods')
    # ### end Alembic commands ###
