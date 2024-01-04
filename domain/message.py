from log import log_action
from openai import OpenAI


class Message:
    def __init__(self, thread, id):
        self.client = OpenAI()
        self.thread = thread
        self.id = id
        self.thread_message = None
        self.content = []
        self.role = None

    def text(self):
        texts = list(content.text.value for content in self.content)
        return " ".join(texts)

    def annotations(self):
        # TODO: Currently the API is not returning annotations
        return list(content.text.annotations for content in self.content)

    @staticmethod
    def create(thread, text):
        if thread is None:
            raise Exception("Thread is required")
        if not text:
            raise Exception("Text is required")

        client = OpenAI()
        thread_message = client.beta.threads.messages.create(
            thread.id,
            role="user",
            content=text,
        )
        new_message = Message.from_raw(thread, thread_message)
        log_action(new_message, "create", new_message)
        return new_message

    @staticmethod
    def retrieve(thread, id):
        client = OpenAI()
        thread_message = client.beta.threads.messages.retrieve(
            message_id=id,
            thread_id=thread.id,
        )
        message = Message.from_raw(thread, thread_message)
        log_action(thread_message, "retrieve", message)
        return message

    @staticmethod
    def from_raw(thread, thread_message):
        message = Message(thread, thread_message.id)
        message.thread_message = thread_message
        message.content = thread_message.content
        message.role = thread_message.role
        return message
