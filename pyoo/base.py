prepositions = ('with/using',
                'at/to',
                # 'in front of',
                'in/inside/into',
                # 'on top of/on/onto/upon',
                # 'out of/from inside/from',
                'over',
                'through',
                'under/underneath/beneath',
                'behind',
                'beside',
                'for/about',
                'is',
                'as',
                'off')
                #'off/off of')

normalized_preps = tuple([x.split('/') for x in prepositions])

# this simple decorator adds verb metadata to a method or function
# verbname is a comma-separated list of verb names with possible woldcard
# dobjspec is 'this' or 'that' or 'none' or 'any' (this = the object which defines the verb, that = an object in the soup, any = any string, none = blank)
# iobjspec is 'this' or 'that' or 'none' or 'any'
# prepspec is one of prepositions strings
# verb prototypes are: (verbname, dobjstr, prepstr, iobjstr, dobj, iobj, argstr)
def verb(verbname, dobjspec, prepspec, iobjspec):
    def verb_decorate(verbfunc):
        names = [x.strip() for x in verbname.split(',')]
        verbfunc.name = names[0]
        verbfunc.names = names
        ps = prepspec
        if isinstance(ps, basestring):
            if ps.find('/') > 0:
                ps = ps.split('/')
            else:
                for p in normalized_preps:
                    if ps in p:
                        ps = p
                        break
        verbfunc.callspec = (dobjspec, ps, iobjspec)
        verbfunc.is_verb = True
        return verbfunc
    return verb_decorate
