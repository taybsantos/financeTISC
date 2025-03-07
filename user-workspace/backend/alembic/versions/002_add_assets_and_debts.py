"""Add assets and debts tables

Revision ID: 002
Revises: 001
Create Date: 2024-02-20 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('cash', 'bank_account', 'investment', 'real_estate', 'vehicle', 
                                 'cryptocurrency', 'stock', 'bond', 'mutual_fund', 'etf', 'retirement', 
                                 'other', name='assettype'), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'pending', 'sold', name='assetstatus'), 
                 nullable=True, default='active'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('acquisition_date', sa.DateTime(), nullable=True),
        sa.Column('acquisition_value', sa.Float(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('last_valuation_date', sa.DateTime(), nullable=True),
        sa.Column('institution', sa.String(), nullable=True),
        sa.Column('account_number', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('ticker_symbol', sa.String(), nullable=True),
        sa.Column('interest_rate', sa.Float(), nullable=True),
        sa.Column('maturity_date', sa.DateTime(), nullable=True),
        sa.Column('property_type', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('square_footage', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('liquidity_level', sa.String(), nullable=True),
        sa.Column('annual_return', sa.Float(), nullable=True),
        sa.Column('total_return', sa.Float(), nullable=True),
        sa.Column('unrealized_gain_loss', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create debts table
    op.create_table(
        'debts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('credit_card', 'student_loan', 'mortgage', 'auto_loan', 'personal_loan',
                                 'business_loan', 'line_of_credit', 'medical_debt', 'other', name='debttype'), 
                 nullable=False),
        sa.Column('status', sa.Enum('current', 'past_due', 'default', 'paid_off', 'in_collection', 'settled',
                                   name='debtstatus'), nullable=True, default='current'),
        sa.Column('original_amount', sa.Float(), nullable=False),
        sa.Column('current_balance', sa.Float(), nullable=False),
        sa.Column('minimum_payment', sa.Float(), nullable=True),
        sa.Column('interest_rate', sa.Float(), nullable=False),
        sa.Column('interest_type', sa.String(), nullable=True),
        sa.Column('apr', sa.Float(), nullable=True),
        sa.Column('payment_frequency', sa.Enum('weekly', 'bi_weekly', 'monthly', 'quarterly', 'annually',
                                             name='paymentfrequency'), nullable=True, default='monthly'),
        sa.Column('payment_amount', sa.Float(), nullable=True),
        sa.Column('next_payment_date', sa.DateTime(), nullable=True),
        sa.Column('last_payment_date', sa.DateTime(), nullable=True),
        sa.Column('last_payment_amount', sa.Float(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('term_months', sa.Integer(), nullable=True),
        sa.Column('remaining_payments', sa.Integer(), nullable=True),
        sa.Column('lender', sa.String(), nullable=True),
        sa.Column('account_number', sa.String(), nullable=True),
        sa.Column('contact_info', sa.String(), nullable=True),
        sa.Column('is_secured', sa.Boolean(), nullable=True, default=False),
        sa.Column('collateral_type', sa.String(), nullable=True),
        sa.Column('collateral_value', sa.Float(), nullable=True),
        sa.Column('payment_history', sa.Text(), nullable=True),
        sa.Column('late_fees', sa.Float(), nullable=True, default=0),
        sa.Column('total_interest_paid', sa.Float(), nullable=True, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_assets_user_id'), 'assets', ['user_id'], unique=False)
    op.create_index(op.f('ix_assets_type'), 'assets', ['type'], unique=False)
    op.create_index(op.f('ix_debts_user_id'), 'debts', ['user_id'], unique=False)
    op.create_index(op.f('ix_debts_type'), 'debts', ['type'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_debts_type'), table_name='debts')
    op.drop_index(op.f('ix_debts_user_id'), table_name='debts')
    op.drop_index(op.f('ix_assets_type'), table_name='assets')
    op.drop_index(op.f('ix_assets_user_id'), table_name='assets')

    # Drop tables
    op.drop_table('debts')
    op.drop_table('assets')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS paymentfrequency')
    op.execute('DROP TYPE IF EXISTS debtstatus')
    op.execute('DROP TYPE IF EXISTS debttype')
    op.execute('DROP TYPE IF EXISTS assetstatus')
    op.execute('DROP TYPE IF EXISTS assettype')
