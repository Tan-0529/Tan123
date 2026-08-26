from app.services.feedback_service import FeedbackService


def test_feedback_add_and_list(tmp_path):
    service = FeedbackService(db_path=str(tmp_path / "feedback.db"))
    service.add("c1", "m1", "like", "不错")
    service.add("c1", "m2", "dislike", "")
    items = service.list()
    assert len(items) == 2
    assert items[0]["rating"] == "dislike"
    assert items[1]["rating"] == "like"
    assert items[1]["comment"] == "不错"


def test_feedback_empty(tmp_path):
    service = FeedbackService(db_path=str(tmp_path / "empty.db"))
    assert service.list() == []
