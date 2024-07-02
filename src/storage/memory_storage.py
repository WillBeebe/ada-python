from storage.storage_manager import StorageManager


class MemoryStorage(StorageManager):
    def __init__(self):
        self._past_messages = []

    def store_message(self, role: str, message: str, **kwargs) -> bool:
        msg = {
            "role": role,
            "content": message
        }
        for key, value in kwargs.items():
            msg[key] = value
        # print(f"storing message {msg}")
        self._past_messages.append(msg)

    def store_raw(self, message: str, **kwargs) -> bool:
        self._past_messages.append(message)

    def get_past_messages(self, id: str=None):
        return self._past_messages.copy()

    def remove_last(self):
        self._past_messages.pop()
