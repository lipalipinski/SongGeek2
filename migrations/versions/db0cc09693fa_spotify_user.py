"""spotify user

Revision ID: db0cc09693fa
Revises: 
Create Date: 2023-01-03 16:32:52.996409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db0cc09693fa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('token', sa.Text(), nullable=True),
    sa.Column('r_token', sa.Text(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###