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

        for term, defs in content:
            for movedef in defs[0][1:]:
                defs.append([movedef])
            defs[0] = defs[0][:1]

    sys.stdout.write(json.dumps(ast))

    return 0

if __name__ == '__main__':
    # pandoc -f rst -t markdown --filter ./vtx_common/tools/pandoc_filter.py -o foo.md foo.rst
    # specify -t json to view the intermediate json ast representation
    sys.exit(main())
