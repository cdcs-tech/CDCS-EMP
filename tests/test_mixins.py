from app.models import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


def test_timestamp_mixin():
    assert hasattr(TimestampMixin, "created_at")
    assert hasattr(TimestampMixin, "updated_at")


def test_audit_mixin():
    assert hasattr(AuditMixin, "created_by")
    assert hasattr(AuditMixin, "updated_by")


def test_soft_delete_mixin():
    assert hasattr(SoftDeleteMixin, "is_deleted")
    assert hasattr(SoftDeleteMixin, "deleted_at")
