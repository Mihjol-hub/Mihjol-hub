"""Added creator relationship and group-keyword association

Revision ID: 32e07277e100
Revises: 66fa1bd500d2
Create Date: 2024-08-09 14:40:47.424476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32e07277e100'
down_revision = '66fa1bd500d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_keyword',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'keyword_id')
    )
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.add_column(sa.Column('creator_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_group_creator', 'users', ['creator_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('creator_id')

    op.drop_table('group_keyword')
    # ### end Alembic commands ###