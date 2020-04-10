"""empty message

Revision ID: 7aef7b7d7cf0
Revises: 56ed7d33de8d
Create Date: 2020-04-02 10:48:30.860726

"""

# revision identifiers, used by Alembic.
revision = '7aef7b7d7cf0'
down_revision = '56ed7d33de8d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_users_student_id'), 'users', ['student_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_student_id'), table_name='users')
    # ### end Alembic commands ###
