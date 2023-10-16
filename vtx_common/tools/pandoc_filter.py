import sys
import json

def walk(elem):
    # https://pandoc.org/using-the-pandoc-api.html#walking-the-ast

    if isinstance(elem, list):
        for subelem in elem:
            yield from walk(subelem)
        return

    if isinstance(elem, dict):
        if 't' in elem:
            yield elem['t'], elem.get('c')
        for v in elem.values():
            yield from walk(v)
        return

def main():

    ast = json.load(sys.stdin)

    # todo: check pandoc-api-version

    for type_, content in walk(ast['blocks']):

        if type_ != 'DefinitionList':
            continue

        # An RST term with multiple definitions gets combined into one -> split
        # ( Only Para types should get split )
        for term, defs in content:

            newdefs = []
            newdef = []

            for def_ in defs[0]:

                if def_['t'] == 'Para' and newdef:
                    # we are on a new paragraph so save the
                    # previous term/def group
                    newdefs.append(newdef.copy())
                    newdef.clear()

                newdef.append(def_)

            if newdef:
                newdefs.append(newdef.copy())

            defs.clear()
            defs.extend(newdefs)

    sys.stdout.write(json.dumps(ast))

    return 0

if __name__ == '__main__':
    # todo: docs on what this is doing and how to use it
    # pandoc -f rst -t markdown --filter ./vtx_common/tools/pandoc_filter.py -o foo.md foo.rst
    # specify -t json to view the intermediate json ast representation
    sys.exit(main())
