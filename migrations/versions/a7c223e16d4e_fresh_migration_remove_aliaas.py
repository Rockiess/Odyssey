"""Fresh Migration-remove-aliaas

Revision ID: a7c223e16d4e
Revises:
Create Date: 2020-05-14 23:14:37.375671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7c223e16d4e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('device') as batch_op:
        batch_op.drop_column('alias')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('device', sa.Column('alias', sa.VARCHAR(length=64), nullable=True))
    # ### end Alembic commands ###
