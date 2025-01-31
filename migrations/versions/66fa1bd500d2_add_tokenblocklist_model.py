"""Add TokenBlocklist model

Revision ID: 66fa1bd500d2
Revises: b5dfbf8eca7b
Create Date: 2024-07-31 16:19:46.462686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66fa1bd500d2'
down_revision = 'b5dfbf8eca7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('token_blocklist', schema=None) as batch_op:
        batch_op.drop_index('ix_token_blocklist_jti')
        batch_op.create_index(batch_op.f('ix_token_blocklist_jti'), ['jti'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('token_blocklist', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_token_blocklist_jti'))
        batch_op.create_index('ix_token_blocklist_jti', ['jti'], unique=False)

    # ### end Alembic commands ###
