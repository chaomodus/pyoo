
from collections import namedtuple

PREPOSITIONS = (
    "with/using",
    "at/to",
    # 'in front of',
    "in/inside/into",
    # 'on top of/on/onto/upon',
    "on/onto/upon",
    # 'out of/from inside/from',
    "from",
    "over",
    "through",
    "under/underneath/beneath",
    "behind",
    "beside",
    "for/about",
    "is",
    "as",
    "off",
)

class PyooError(Exception):
    pass


class PyooVerbNotFound(PyooError):
    pass

class PyooObjectNotFound(PyooError):
    pass

NORMALIZED_PREPS = tuple([x.split("/") for x in PREPOSITIONS])

VerbCallFrame = namedtuple("VerbCallFrame", "environment,verbname,dobj,dobjstr,prepstr,iobj,iobjstr,argstr")

# this simple decorator adds verb metadata to a method or function
# verbname is a comma-separated list of verb names with possible woldcard
# dobjspec is 'this' or 'that' or 'none' or 'any' (this = the object which defines the verb, that = an object in the
#   soup, any = any string, none = blank)
# iobjspec is 'this' or 'that' or 'none' or 'any'
# prepspec is one of prepositions strings
# verb prototypes are: (verb_callframe, argstr)

def make_verb(verbname, dobjspec, prepspec, iobjspec):
    def verb_decorate(verbfunc):
        names = [x.strip() for x in verbname.split(",")]
        verbfunc.name = names[0]
        verbfunc.names = names
        ps = prepspec
        if isinstance(ps, str):
            if ps.find("/") > 0:
                ps = ps.split("/")
            else:
                for p in NORMALIZED_PREPS:
                    if ps in p:
                        ps = p
                        break
        verbfunc.callspec = (dobjspec, ps, iobjspec)
        verbfunc.is_verb = True
        return verbfunc

    return verb_decorate
