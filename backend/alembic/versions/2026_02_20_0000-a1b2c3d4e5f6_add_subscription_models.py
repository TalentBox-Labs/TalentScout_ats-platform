"""Add subscription models

Revision ID: 2026_02_20_0000-a1b2c3d4e5f6
Revises: 2026_02_19_0000_add_super_admin_field
Create Date: 2026-02-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_02_20_0000-a1b2c3d4e5f6'
down_revision = '2026_02_19_0000_add_super_admin_field'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    subscriptionplan = sa.Enum('free', 'starter', 'pro', 'enterprise', name='subscriptionplan')
    subscriptionstatus = sa.Enum('active', 'past_due', 'cancelled', 'trialing', name='subscriptionstatus')
    paymentgateway = sa.Enum('razorpay', 'stripe', name='paymentgateway')
    transactionstatus = sa.Enum('pending', 'success', 'failed', 'refunded', name='transactionstatus')

    subscriptionplan.create(op.get_bind(), checkfirst=True)
    subscriptionstatus.create(op.get_bind(), checkfirst=True)
    paymentgateway.create(op.get_bind(), checkfirst=True)
    transactionstatus.create(op.get_bind(), checkfirst=True)

    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('plan', sa.Enum('free', 'starter', 'pro', 'enterprise', name='subscriptionplan'), nullable=False, server_default=sa.text("'free'")),
        sa.Column('status', sa.Enum('active', 'past_due', 'cancelled', 'trialing', name='subscriptionstatus'), nullable=False, server_default=sa.text("'trialing'")),
        sa.Column('payment_gateway', sa.Enum('razorpay', 'stripe', name='paymentgateway'), nullable=True),
        sa.Column('gateway_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('gateway_customer_id', sa.String(length=255), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_org_id', 'subscriptions', ['org_id'], unique=False)
    op.create_index('ix_subscriptions_gateway_subscription_id', 'subscriptions', ['gateway_subscription_id'], unique=False)

    # Create payment_transactions table
    op.create_table('payment_transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('subscription_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('gateway', sa.Enum('razorpay', 'stripe', name='paymentgateway'), nullable=False),
        sa.Column('gateway_payment_id', sa.String(length=255), nullable=True),
        sa.Column('gateway_order_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('pending', 'success', 'failed', 'refunded', name='transactionstatus'), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payment_transactions_org_id', 'payment_transactions', ['org_id'], unique=False)
    op.create_index('ix_payment_transactions_gateway_payment_id', 'payment_transactions', ['gateway_payment_id'], unique=False)

    # Add subscription_id column to organizations
    op.add_column('organizations', sa.Column('subscription_id', sa.String(), sa.ForeignKey('subscriptions.id', ondelete='SET NULL'), nullable=True))


def downgrade() -> None:
    # Drop subscription_id column from organizations
    op.drop_column('organizations', 'subscription_id')

    # Drop payment_transactions table and indexes
    op.drop_index('ix_payment_transactions_gateway_payment_id', table_name='payment_transactions')
    op.drop_index('ix_payment_transactions_org_id', table_name='payment_transactions')
    op.drop_table('payment_transactions')

    # Drop subscriptions table and indexes
    op.drop_index('ix_subscriptions_gateway_subscription_id', table_name='subscriptions')
    op.drop_index('ix_subscriptions_org_id', table_name='subscriptions')
    op.drop_table('subscriptions')

    # Drop enum types
    sa.Enum(name='transactionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymentgateway').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionplan').drop(op.get_bind(), checkfirst=True)