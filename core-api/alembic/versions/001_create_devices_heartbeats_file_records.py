"""create devices heartbeats file_records

Revision ID: 001
Revises: 
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('plotter_type', sa.String(), nullable=False),
        sa.Column('api_key_hash', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    op.create_index(op.f('ix_devices_device_id'), 'devices', ['device_id'], unique=True)
    
    # Create heartbeats table
    op.create_table(
        'heartbeats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('queue_size', sa.Integer(), nullable=True),
        sa.Column('last_upload_ok', sa.Boolean(), nullable=True),
        sa.Column('connector_version', sa.String(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heartbeats_id'), 'heartbeats', ['id'], unique=False)
    op.create_index(op.f('ix_heartbeats_device_id'), 'heartbeats', ['device_id'], unique=False)
    
    # Create file_records table
    op.create_table(
        'file_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('source_format', sa.String(), nullable=False),
        sa.Column('local_path', sa.String(), nullable=True),
        sa.Column('remote_path', sa.String(), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('processing_status', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_records_id'), 'file_records', ['id'], unique=False)
    op.create_index(op.f('ix_file_records_device_id'), 'file_records', ['device_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_file_records_device_id'), table_name='file_records')
    op.drop_index(op.f('ix_file_records_id'), table_name='file_records')
    op.drop_table('file_records')
    op.drop_index(op.f('ix_heartbeats_device_id'), table_name='heartbeats')
    op.drop_index(op.f('ix_heartbeats_id'), table_name='heartbeats')
    op.drop_table('heartbeats')
    op.drop_index(op.f('ix_devices_device_id'), table_name='devices')
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')

