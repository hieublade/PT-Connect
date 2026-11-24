import pytest
from app.core.exceptions import BadRequestException, ResourceNotFoundException
from app.models.enums import Role, UserStatus
from app.models.user import Student, PT
from app.schemas.requests.chat import SendMessageRequest
from app.services.chat_service import ChatService


def test_chat_send_and_get_messages(db_session):
    student = Student(
        full_name="Nguyễn Văn Học Viên",
        email="student.chat@test.com",
        password_hash="hashed",
        phone="0911000111",
        role=Role.STUDENT,
        status=UserStatus.ACTIVE,
    )
    pt = PT(
        full_name="Trần Văn Huấn Luyện Viên",
        email="pt.chat@test.com",
        password_hash="hashed",
        phone="0911000222",
        role=Role.PT,
        status=UserStatus.ACTIVE,
    )
    db_session.add_all([student, pt])
    db_session.commit()

    service = ChatService(db_session)

    # 1. Send message from student to PT
    req = SendMessageRequest(receiver_id=pt.id, content="Chào HLV, tôi muốn hỏi về lịch tập tuần này.")
    sent = service.send_message(student, req)
    assert sent.id is not None
    assert sent.sender_id == student.id
    assert sent.receiver_id == pt.id
    assert sent.content == "Chào HLV, tôi muốn hỏi về lịch tập tuần này."
    assert sent.is_read is False

    # 2. Check conversation list for PT
    conversations = service.get_conversations(pt)
    assert len(conversations) == 1
    assert conversations[0].partner_id == student.id
    assert conversations[0].unread_count == 1
    assert conversations[0].last_message == "Chào HLV, tôi muốn hỏi về lịch tập tuần này."

    # 3. PT reads messages -> is_read should become True
    msgs = service.get_messages(pt, student.id)
    assert len(msgs) == 1
    assert msgs[0].content == "Chào HLV, tôi muốn hỏi về lịch tập tuần này."

    # Unread count should now be 0
    conversations_after = service.get_conversations(pt)
    assert conversations_after[0].unread_count == 0

    # 4. PT replies to student
    reply_req = SendMessageRequest(receiver_id=student.id, content="Chào bạn, lịch tập thứ 3 và thứ 5 vẫn diễn ra bình thường nhé.")
    reply = service.send_message(pt, reply_req)
    assert reply.sender_id == pt.id
    assert reply.receiver_id == student.id

    # 5. Check full conversation history
    full_history = service.get_messages(student, pt.id)
    assert len(full_history) == 2


def test_chat_validation_errors(db_session):
    student = Student(
        full_name="Nguyễn Văn A",
        email="student.val@test.com",
        password_hash="hashed",
        phone="0911999888",
        role=Role.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(student)
    db_session.commit()

    service = ChatService(db_session)

    # Cannot send message to self
    with pytest.raises(BadRequestException):
        service.send_message(student, SendMessageRequest(receiver_id=student.id, content="Hello me"))

    # Cannot send message to non-existent user
    with pytest.raises(ResourceNotFoundException):
        service.send_message(student, SendMessageRequest(receiver_id=999999, content="Hello"))
