from log import log_action
from openai import OpenAI
from domain.message import Message


class Thread:
    def __init__(self, id):
        self.client = OpenAI()
        self.id = id
        self.name = None
        self._thread = None
        self.messages = []

    def create(self, name):
        empty_thread = self.client.beta.threads.create()
        self.id = empty_thread.id
        self.name = name
        self._thread = empty_thread
        log_action(self, "create", empty_thread)

    def retrieve(self):
        thread = self.client.beta.threads.retrieve(self.id)
        self._thread = thread
        log_action(self, "retrieve", thread)
        return self

    def delete(self):
        response = self.client.beta.threads.delete(self.id)
        log_action(self, "delete", response)

    def retrieve_messages(
        self,
        limit=None,
        order=None,
        before=None,
        after=None,
    ):
        limit = limit or 100
        order = order or "desc"

        thread_messages = self.client.beta.threads.messages.list(
            thread_id=self.id,
            limit=limit,
            order=order,
            before=before,
            after=after,
        )

        # transform raw messages into Message objects
        messages = []
        for thread_message in thread_messages.data:
            message = Message.from_raw(self, thread_message)
            messages.append(message)

        self.messages = messages

        log_action(self, "retrieve_messages", messages)

        return messages

    def retrieve_message_and_append(self, message_id):
        message = Message.retrieve(self, message_id)
        self.messages.append(message)
        return message

    def to_json(self):
        return {"id": self.id, "name": self.name}
