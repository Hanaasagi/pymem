from pymem.summary import get_summary
from multiprocessing import Process, Event


def test_get_summary():
    def sleep_until_wake(e):
        e.wait()

    e = Event()
    p = Process(target=sleep_until_wake, args=(e,))
    p.start()
    pid = p.pid
    summary = get_summary(pid)
    e.set()
    p.join()

    assert len(summary) == 4
    assert set(summary.keys()) == set(["private", "shared", "total", "swap"])

    def convert(value):
        return float(value[:-4])  # remove unit. e.g '1.00 MiB' to '1.00'

    private, shared, total, *_ = map(convert, summary.values())
    assert abs(private + shared - total) <= 0.1
