import sys

verb_list = ['get', 'set', 'delete']


def commit():
    print('committed')


def main(argv):
    if not (4 <= len(argv) <= 5):
        # usage()
        # return BAD_ARGS
        return "BAD ARGS"
    dbname, verb, key, value = (argv[1:] + [None])[:4]
    if verb not in verb_list:
        # usage()
        # return BAD_VERB
        return "BAD VERB"
    # db = fbdb.connet(dbname)
    db = {'commit': commit}
    try:
        if verb == 'get':
            sys.stdout.write(db[key])
        elif verb == 'set':
            db[key] = value
            db.commit()
        else:
            del db[key]
            db.commit()
    except KeyError:
        print("key not found", file=sys.stderr)
        # return BAD_KEY
        return "BAD_KEY"
    # return OK
    return "OK"


main(sys.argv)
