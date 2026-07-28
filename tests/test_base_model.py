from app.models import BaseModel


def test_base_model_has_id():
    assert hasattr(BaseModel, "id")
