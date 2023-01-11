"""wywalam nullable=false z playlist

Revision ID: f1aa13fab80e
Revises: 2fe3cb366bdf
Create Date: 2023-01-11 18:33:13.760816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1aa13fab80e'
down_revision = '2fe3cb366bdf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('url',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('updated',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.alter_column('updated',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.alter_column('url',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###
