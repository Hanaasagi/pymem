import gc
import json
from sys import getsizeof
from inspect import stack
from inspect import isframe

f = globals().get("f")
limit = globals().get("limit")

_Py_TPFLAGS_HAVE_GC = 1 << 14  # Py_TPFLAGS_HAVE_GC


def _is_containerobject(obj):
    """Is the passed object a container object."""
    return bool(getattr(type(obj), "__flags__", 0) & _Py_TPFLAGS_HAVE_GC)


def ignore_object(obj):
    try:
        return isframe(obj)
    except ReferenceError:
        return True


def _remove_duplicates(objects):
    """Remove duplicate objects.

    Inspired by http://www.peterbe.com/plog/uniqifiers-benchmark

    """
    seen = set()
    result = []
    for item in objects:
        marker = id(item)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(item)
    return result


def get_referents(object, level=1):
    """Get all referents of an object up to a certain level.

    The referents will not be returned in a specific order and
    will not contain duplicate objects. Duplicate objects will be removed.

    Keyword arguments:
    level -- level of indirection to which referents considered.

    This function is recursive.

    """
    res = gc.get_referents(object)
    level -= 1
    if level > 0:
        for obj in res:
            res.extend(get_referents(obj, level))
    res = _remove_duplicates(res)
    return res


def get_objects(remove_dups=True, include_frames=False):
    gc.collect()
    # Do not initialize local variables before calling gc.get_objects or those
    # will be included in the list. Furthermore, ignore frame objects to
    # prevent reference cycles.
    tmp = gc.get_objects()
    tmp = [obj for obj in tmp if not ignore_object(obj)]

    res = []
    for obj in tmp:
        # gc.get_objects returns only container objects, but we also want
        # the objects referenced by them
        refs = get_referents(obj)
        for ref in refs:
            if not _is_containerobject(ref):
                # we already got the container objects, now we only add
                # non-container objects
                res.append(ref)
    res.extend(tmp)
    if remove_dups:
        res = _remove_duplicates(res)

    if include_frames:
        for sf in stack()[2:]:
            res.append(sf[0])
    return res


def summarize(objects):
    """Summarize an objects list.

    Return a list of lists, whereas each row consists of::
      [str(type), number of objects of this type, total size of these objects].

    No guarantee regarding the order is given.

    """
    count = {}
    total_size = {}
    for obj in objects:
        otype = type(obj)
        if otype in count:
            count[otype] += 1
            total_size[otype] += getsizeof(obj)
        else:
            count[otype] = 1
            total_size[otype] = getsizeof(obj)
    rows = []
    for otype in count:
        rows.append([otype, count[otype], total_size[otype]])
    return rows


def human(num, power="B"):
    powers = ["B", "Ki", "Mi", "Gi", "Ti"]
    while num >= 1024.0:
        num /= 1024.0
        power = powers[powers.index(power) + 1]
    return "%.2f %sB" % (num, power)


def format_(rows, limit=15, sort="size", order="descending"):
    """Format the rows as a summary.

    Keyword arguments:
    limit -- the maximum number of elements to be listed
    sort  -- sort elements by 'size', 'type', or '#'
    order -- sort 'ascending' or 'descending'
    """
    localrows = []
    for row in rows:
        localrows.append(list(row))
    # input validation
    sortby = ["type", "#", "size"]
    if sort not in sortby:
        raise ValueError("invalid sort, should be one of" + str(sortby))
    orders = ["ascending", "descending"]
    if order not in orders:
        raise ValueError("invalid order, should be one of" + str(orders))
    # sort rows
    if sortby.index(sort) == 0:
        if order == "ascending":
            localrows.sort(key=lambda x: type(x[0]))
        elif order == "descending":
            localrows.sort(key=lambda x: type(x[0]), reverse=True)
    else:
        if order == "ascending":
            localrows.sort(key=lambda x: x[sortby.index(sort)])
        elif order == "descending":
            localrows.sort(key=lambda x: x[sortby.index(sort)], reverse=True)
    # limit rows
    localrows = localrows[0:limit]
    for row in localrows:
        row[2] = human(row[2])
    rtn = []
    for row in localrows:
        rtn.append(
            {"type": str(row[0]), "objects": row[1], "total_size": row[2]}
        )
    return rtn


all_objects = get_objects()
# f.write(str(gc.garbage))
# f.write("\n")
s = summarize(all_objects)
json.dump(format_(s, limit=limit), f)
