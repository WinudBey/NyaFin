import threading

class StateManager:
    _state = {}
    _lock = threading.Lock()
    _cancel_flags = {}

    @classmethod
    def set_status(cls, series_name, episode, status, progress=0, detail=""):
        with cls._lock:
            if series_name not in cls._state:
                cls._state[series_name] = {}
            cls._state[series_name][episode] = {
                "status": status,
                "progress": progress,
                "detail": detail
            }

    @classmethod
    def get_state(cls):
        with cls._lock:
            # Return a copy to avoid mutation issues
            return {s: ep.copy() for s, ep in cls._state.items()}

    @classmethod
    def request_cancel(cls, series_name, episode):
        with cls._lock:
            cls._cancel_flags[f"{series_name}_{episode}"] = True

    @classmethod
    def is_cancelled(cls, series_name, episode):
        with cls._lock:
            return cls._cancel_flags.get(f"{series_name}_{episode}", False)

    @classmethod
    def clear_cancel(cls, series_name, episode):
        with cls._lock:
            cls._cancel_flags.pop(f"{series_name}_{episode}", None)

    @classmethod
    def remove_task(cls, series_name, episode):
        with cls._lock:
            if series_name in cls._state and episode in cls._state[series_name]:
                del cls._state[series_name][episode]
                if not cls._state[series_name]:
                    del cls._state[series_name]
            cls.clear_cancel(series_name, episode)
