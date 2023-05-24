from pydantic import BaseModel


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    chat: Chat
    text: str | None = None


class EditedMessage(BaseModel):
    chat: Chat
    text: str | None = None


class UpdateObj(BaseModel):
    update_id: int
    message: Message | None
    edited_message: EditedMessage | None


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: list[UpdateObj]


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message
