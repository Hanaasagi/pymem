import gc
import json

f = globals().get("f")
gc.collect()
garbage = gc.garbage
info = {"count": len(garbage), "objects": garbage}

json.dump(info, f)
