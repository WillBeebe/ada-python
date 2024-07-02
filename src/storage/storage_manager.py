from abc import ABC, abstractmethod


class StorageManager(ABC):
    def __init__(self):
        self.get_past_messages_callback = None
        self.store_message_callback = None
        self.store_raw_callback = None

    @abstractmethod
    def store_message(self, role: str, message: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def store_raw(self, message: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_past_messages(self):
        pass

    @abstractmethod
    def remove_last(self):
        pass

    def set_get_past_messages_callback(self, callback):
        self.get_past_messages_callback = callback

    def set_store_message_callback(self, callback):
        self.store_message_callback = callback

    def set_store_raw_callback(self, callback):
        self.store_raw_callback = callback
