"""initial migration

Revision ID: 001
Create Date: 2025-01-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_table(
        'account_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service_type', sa.Enum('kubernetes', 'docker', 'cloudwatch', 'grafana', 'sentry', name='servicetype'), nullable=False),
        sa.Column('credentials_encrypted', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSON()),
        sa.Column('status', sa.Enum('active', 'inactive', 'error', name='connectionstatus'), default='active'),
        sa.Column('last_tested', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )

    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='severity'), default='medium'),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('logs_json', postgresql.JSON()),
        sa.Column('correlation_data', postgresql.JSON()),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('resolved', sa.DateTime()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )

def downgrade() -> None:
    op.drop_table('incidents')
    op.drop_table('account_connections')
    op.drop_table('projects')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS severity')
    op.execute('DROP TYPE IF EXISTS connectionstatus')
    op.execute('DROP TYPE IF EXISTS servicetype')