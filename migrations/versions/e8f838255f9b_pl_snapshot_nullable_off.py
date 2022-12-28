"""pl snapshot nullable off

Revision ID: e8f838255f9b
Revises: e6ee6a101b34
Create Date: 2022-12-28 12:32:26.848836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8f838255f9b'
down_revision = 'e6ee6a101b34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.alter_column('snapshot_id',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.alter_column('snapshot_id',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###
