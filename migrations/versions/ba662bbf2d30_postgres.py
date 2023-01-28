"""postgres

Revision ID: ba662bbf2d30
Revises: 
Create Date: 2023-01-25 19:30:10.934359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba662bbf2d30'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_artist_id'), ['id'], unique=False)

    op.create_table('img',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sm', sa.Text(), nullable=False),
    sa.Column('md', sa.Text(), nullable=False),
    sa.Column('lg', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('img', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_img_id'), ['id'], unique=False)

    op.create_table('owner',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('owner', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_owner_id'), ['id'], unique=False)

    op.create_table('album',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('img_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['img_id'], ['img.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('album', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_album_id'), ['id'], unique=False)

    op.create_table('playlist',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('snapshot_id', sa.Text(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Text(), nullable=True),
    sa.Column('img_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['img_id'], ['img.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['owner.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_playlist_id'), ['id'], unique=False)

    op.create_table('user',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('token', sa.Text(), nullable=True),
    sa.Column('r_token', sa.Text(), nullable=True),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('img_id', sa.Integer(), nullable=True),
    sa.Column('total_points', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['img_id'], ['img.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_id'), ['id'], unique=False)

    op.create_table('album_artist',
    sa.Column('album_id', sa.Text(), nullable=False),
    sa.Column('artist_id', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.PrimaryKeyConstraint('album_id', 'artist_id')
    )
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Text(), nullable=True),
    sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True),
    sa.Column('playlist_id', sa.Text(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('final_points', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlist.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_game_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_game_user_id'), ['user_id'], unique=False)

    op.create_table('track',
    sa.Column('id', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('album_id', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('prev_url', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('track', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_track_id'), ['id'], unique=False)

    op.create_table('playlist_track',
    sa.Column('playlist_id', sa.Text(), nullable=False),
    sa.Column('track_id', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlist.id'], ),
    sa.ForeignKeyConstraint(['track_id'], ['track.id'], ),
    sa.PrimaryKeyConstraint('playlist_id', 'track_id')
    )
    op.create_table('quest',
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('track_id', sa.Text(), nullable=True),
    sa.Column('q_num', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['track_id'], ['track.id'], ),
    sa.PrimaryKeyConstraint('game_id', 'q_num')
    )
    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_quest_game_id'), ['game_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_quest_track_id'), ['track_id'], unique=False)

    op.create_table('track_artist',
    sa.Column('track_id', sa.Text(), nullable=False),
    sa.Column('artist_id', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['track_id'], ['track.id'], ),
    sa.PrimaryKeyConstraint('track_id', 'artist_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('track_artist')
    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_quest_track_id'))
        batch_op.drop_index(batch_op.f('ix_quest_game_id'))

    op.drop_table('quest')
    op.drop_table('playlist_track')
    with op.batch_alter_table('track', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_track_id'))

    op.drop_table('track')
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_game_user_id'))
        batch_op.drop_index(batch_op.f('ix_game_id'))

    op.drop_table('game')
    op.drop_table('album_artist')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_id'))

    op.drop_table('user')
    with op.batch_alter_table('playlist', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_playlist_id'))

    op.drop_table('playlist')
    with op.batch_alter_table('album', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_album_id'))

    op.drop_table('album')
    with op.batch_alter_table('owner', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_owner_id'))

    op.drop_table('owner')
    with op.batch_alter_table('img', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_img_id'))

    op.drop_table('img')
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_artist_id'))

    op.drop_table('artist')
    # ### end Alembic commands ###