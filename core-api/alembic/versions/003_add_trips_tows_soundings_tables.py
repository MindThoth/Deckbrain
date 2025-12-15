"""add trips tows soundings tables

Revision ID: 003
Revises: 272465ebd1ab
Create Date: 2025-12-14 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '272465ebd1ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create trips table
    op.create_table(
        'trips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('min_lat', sa.Float(), nullable=True),
        sa.Column('max_lat', sa.Float(), nullable=True),
        sa.Column('min_lon', sa.Float(), nullable=True),
        sa.Column('max_lon', sa.Float(), nullable=True),
        sa.Column('distance_nm', sa.Float(), nullable=True),
        sa.Column('duration_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trips_id'), 'trips', ['id'], unique=False)
    op.create_index(op.f('ix_trips_device_id'), 'trips', ['device_id'], unique=False)
    op.create_index(op.f('ix_trips_start_time'), 'trips', ['start_time'], unique=False)
    op.create_index(op.f('ix_trips_end_time'), 'trips', ['end_time'], unique=False)
    
    # Create tows table
    op.create_table(
        'tows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trip_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('start_lat', sa.Float(), nullable=True),
        sa.Column('start_lon', sa.Float(), nullable=True),
        sa.Column('end_lat', sa.Float(), nullable=True),
        sa.Column('end_lon', sa.Float(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('tow_number', sa.Integer(), nullable=True),
        sa.Column('distance_nm', sa.Float(), nullable=True),
        sa.Column('duration_hours', sa.Float(), nullable=True),
        sa.Column('avg_depth_m', sa.Float(), nullable=True),
        sa.Column('min_depth_m', sa.Float(), nullable=True),
        sa.Column('max_depth_m', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tows_id'), 'tows', ['id'], unique=False)
    op.create_index(op.f('ix_tows_trip_id'), 'tows', ['trip_id'], unique=False)
    op.create_index(op.f('ix_tows_start_time'), 'tows', ['start_time'], unique=False)
    op.create_index(op.f('ix_tows_end_time'), 'tows', ['end_time'], unique=False)
    
    # Create soundings table
    op.create_table(
        'soundings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('trip_id', sa.Integer(), nullable=True),
        sa.Column('tow_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('depth', sa.Float(), nullable=False),
        sa.Column('water_temp', sa.Float(), nullable=True),
        sa.Column('speed_knots', sa.Float(), nullable=True),
        sa.Column('course_deg', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.id'], ),
        sa.ForeignKeyConstraint(['tow_id'], ['tows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_soundings_id'), 'soundings', ['id'], unique=False)
    op.create_index(op.f('ix_soundings_device_id'), 'soundings', ['device_id'], unique=False)
    op.create_index(op.f('ix_soundings_trip_id'), 'soundings', ['trip_id'], unique=False)
    op.create_index(op.f('ix_soundings_tow_id'), 'soundings', ['tow_id'], unique=False)
    op.create_index(op.f('ix_soundings_timestamp'), 'soundings', ['timestamp'], unique=False)
    op.create_index('ix_soundings_device_timestamp', 'soundings', ['device_id', 'timestamp'], unique=False)
    op.create_index('ix_soundings_trip_timestamp', 'soundings', ['trip_id', 'timestamp'], unique=False)
    op.create_index('ix_soundings_location', 'soundings', ['latitude', 'longitude'], unique=False)


def downgrade() -> None:
    # Drop soundings table
    op.drop_index('ix_soundings_location', table_name='soundings')
    op.drop_index('ix_soundings_trip_timestamp', table_name='soundings')
    op.drop_index('ix_soundings_device_timestamp', table_name='soundings')
    op.drop_index(op.f('ix_soundings_timestamp'), table_name='soundings')
    op.drop_index(op.f('ix_soundings_tow_id'), table_name='soundings')
    op.drop_index(op.f('ix_soundings_trip_id'), table_name='soundings')
    op.drop_index(op.f('ix_soundings_device_id'), table_name='soundings')
    op.drop_index(op.f('ix_soundings_id'), table_name='soundings')
    op.drop_table('soundings')
    
    # Drop tows table
    op.drop_index(op.f('ix_tows_end_time'), table_name='tows')
    op.drop_index(op.f('ix_tows_start_time'), table_name='tows')
    op.drop_index(op.f('ix_tows_trip_id'), table_name='tows')
    op.drop_index(op.f('ix_tows_id'), table_name='tows')
    op.drop_table('tows')
    
    # Drop trips table
    op.drop_index(op.f('ix_trips_end_time'), table_name='trips')
    op.drop_index(op.f('ix_trips_start_time'), table_name='trips')
    op.drop_index(op.f('ix_trips_device_id'), table_name='trips')
    op.drop_index(op.f('ix_trips_id'), table_name='trips')
    op.drop_table('trips')

