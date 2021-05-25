"""empty message

Revision ID: 7d2ee349d130
Revises: e1c5ed1cd1cd
Create Date: 2021-05-24 00:30:10.782496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2ee349d130'
down_revision = 'e1c5ed1cd1cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('list_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'todos', 'todolists', ['list_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'todos', type_='foreignkey')
    op.drop_column('todos', 'list_id')
    # ### end Alembic commands ###