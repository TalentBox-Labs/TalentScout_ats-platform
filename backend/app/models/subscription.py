"""Subscription and payment models."""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, JSON, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base import TimeStampMixin, generate_uuid


class SubscriptionPlan(str, enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status types."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIALING = "trialing"


class PaymentGateway(str, enum.Enum):
    """Payment gateway types."""
    RAZORPAY = "razorpay"
    STRIPE = "stripe"


class TransactionStatus(str, enum.Enum):
    """Payment transaction status types."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Subscription(Base, TimeStampMixin):
    """Subscription model."""

    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    payment_gateway = Column(SQLEnum(PaymentGateway), nullable=True)
    gateway_subscription_id = Column(String(255), nullable=True, index=True)
    gateway_customer_id = Column(String(255), nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="subscription", uselist=False)
    transactions = relationship("PaymentTransaction", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.id} for org {self.org_id}>"


class PaymentTransaction(Base, TimeStampMixin):
    """Payment transaction model."""

    __tablename__ = "payment_transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    org_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    gateway_payment_id = Column(String(255), nullable=True, index=True)
    gateway_order_id = Column(String(255), nullable=True)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    metadata = Column(JSON, nullable=True, default=dict)

    # Relationships
    organization = relationship("Organization", back_populates="payment_transactions")
    subscription = relationship("Subscription", back_populates="transactions")

    def __repr__(self):
        return f"<PaymentTransaction {self.id} amount {self.amount} {self.currency}>"