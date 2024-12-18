"""Initial migration

Revision ID: 4dc222c76d0f
Revises: 
Create Date: 2024-11-29 13:49:47.907129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dc222c76d0f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('individuals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('birth_place', sa.String(length=100), nullable=True),
    sa.Column('death_date', sa.Date(), nullable=True),
    sa.Column('death_place', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('individuals', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_individuals_birth_place'), ['birth_place'], unique=False)
        batch_op.create_index(batch_op.f('ix_individuals_death_place'), ['death_place'], unique=False)
        batch_op.create_index(batch_op.f('ix_individuals_user_id'), ['user_id'], unique=False)

    op.create_table('families',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('partner1_id', sa.Integer(), nullable=False),
    sa.Column('partner2_id', sa.Integer(), nullable=False),
    sa.Column('relationship_type', sa.Enum('MARRIAGE', 'CIVIL_UNION', 'PARTNERSHIP', 'OTHER', name='relationshiptypeenum'), nullable=True),
    sa.Column('union_date', sa.Date(), nullable=True),
    sa.Column('union_place', sa.String(length=100), nullable=True),
    sa.Column('dissolution_date', sa.Date(), nullable=True),
    sa.CheckConstraint('dissolution_date IS NULL OR dissolution_date > union_date', name='chk_dissolution_after_union'),
    sa.CheckConstraint('partner1_id < partner2_id', name='chk_partner_order'),
    sa.ForeignKeyConstraint(['partner1_id'], ['individuals.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['partner2_id'], ['individuals.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('partner1_id', 'partner2_id', name='uix_partners')
    )
    with op.batch_alter_table('families', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_families_partner1_id'), ['partner1_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_families_partner2_id'), ['partner2_id'], unique=False)

    op.create_table('identities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('individual_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'TRANSGENDER', 'GENDER_NEUTRAL', 'NON_BINARY', 'AGENDER', 'PANGENDER', 'GENDERQUEER', 'TWO_SPIRIT', 'THIRD_GENDER', 'OTHER', 'UNKNOWN', name='genderenum'), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.CheckConstraint('valid_until IS NULL OR valid_until > valid_from', name='chk_validity_dates'),
    sa.ForeignKeyConstraint(['individual_id'], ['individuals.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('individual_id', 'valid_from', 'valid_until', name='uix_identity_validity')
    )
    with op.batch_alter_table('identities', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_identities_individual_id'), ['individual_id'], unique=False)

    op.create_table('relationships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('child_id', sa.Integer(), nullable=False),
    sa.Column('relationship_type', sa.Enum('PARENT', 'GUARDIAN', 'CHILD', name='relationshiptype'), nullable=False),
    sa.CheckConstraint('parent_id != child_id', name='chk_parent_child_not_same'),
    sa.ForeignKeyConstraint(['child_id'], ['individuals.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_id'], ['individuals.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('parent_id', 'child_id', 'relationship_type', name='uix_relationship')
    )
    with op.batch_alter_table('relationships', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_relationships_child_id'), ['child_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_relationships_parent_id'), ['parent_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('relationships', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_relationships_parent_id'))
        batch_op.drop_index(batch_op.f('ix_relationships_child_id'))

    op.drop_table('relationships')
    with op.batch_alter_table('identities', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_identities_individual_id'))

    op.drop_table('identities')
    with op.batch_alter_table('families', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_families_partner2_id'))
        batch_op.drop_index(batch_op.f('ix_families_partner1_id'))

    op.drop_table('families')
    with op.batch_alter_table('individuals', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_individuals_user_id'))
        batch_op.drop_index(batch_op.f('ix_individuals_death_place'))
        batch_op.drop_index(batch_op.f('ix_individuals_birth_place'))

    op.drop_table('individuals')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    # ### end Alembic commands ###
