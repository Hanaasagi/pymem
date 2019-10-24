import gc
import json


def main():
    f = globals().get("f")
    gc.collect()
    garbage = gc.garbage
    result = {"count": len(garbage), "objects": garbage}
    json.dump(result, f)


main()
