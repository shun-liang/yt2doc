import time


class Timer:
    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        self.seconds = time.perf_counter() - self._start
