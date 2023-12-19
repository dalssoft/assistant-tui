from domain.thread import Thread
import json
from log import log_action


class ThreadList:
    def __init__(self, scope: str):
        self.scope = scope
        self.file_name = f"threads_{self.scope}.json"

    def _persist(self, threads):
        file = open(self.file_name, "w")
        file.write(json.dumps(threads, default=lambda x: x.to_json()))
        file.close()

    def _read(self):
        try:
            file = open(self.file_name, "r")
            return json.loads(file.read())
        except:
            return []

    def _add_thread(self, thread):
        threads = self._read()
        threads.append(thread)
        self._persist(threads)

    def create_thread(self, name):
        thread = Thread(id=None)
        thread.create(name)
        self._add_thread(thread)
        log_action(ThreadList, "create_thread", thread)
        return thread

    def remove_thread(self, id):
        threads = self._read()
        log_action(ThreadList, "remove_thread", id)
        for thread in threads:
            if thread["id"] == id:
                threads.remove(thread)
                Thread(id=id).delete()
                self._persist(threads)
                return True
        return False

    def list_all(self):
        threads_data = self._read()
        threads = []
        for thread_data in threads_data:
            thread = Thread(id=thread_data["id"])
            thread.name = thread_data["name"]
            threads.append(thread)
        log_action(ThreadList, "list_all", threads)
        return threads
