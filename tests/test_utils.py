from multiprocessing import Process, Event
from pymem.utils import human
from pymem.utils import check_process_exist


def test_human():
    assert human(1024 * 1024) == "1024.00"
    assert human(1024 * 1024, dst_unit="GiB") == "1.00"
    assert human(1024 * 1024, dst_unit="GiB", include_unit=True) == "1.00 GiB"
    assert human(1024, src_unit="MiB", dst_unit="KiB") == "1048576.00"


def test_check_process_exist():
    def sleep_until_wake(e):
        e.wait()

    e = Event()
    p = Process(target=sleep_until_wake, args=(e,))
    p.start()
    pid = p.pid
    assert check_process_exist(pid) is True
    e.set()
    p.join()
    # FIXME race condition
    assert check_process_exist(pid) is False
