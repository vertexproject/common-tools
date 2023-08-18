import sys
import subprocess

# Replace the embedded commit information with our current git commit
# Takes the file path as a single argument.

def main(argv):
    filepath = argv[0]
    try:
        ret = subprocess.run(['git', 'rev-parse', 'HEAD'],
                             capture_output=True,
                             timeout=15,
                             check=True,
                             text=True,)
    except Exception as e:
        print(f'Error grabbing commit: {e}')
        return 1
    else:
        commit = ret.stdout.strip()
    with open(filepath, 'r') as fd:
        content = fd.read()
    new_content = content.replace("commit = ''", f"commit = '{commit}'")
    if content == new_content:
        print(f'Unable to insert commit into {filepath}')
        return 1
    with open(filepath, 'wb') as fd:
        _ = fd.write(new_content.encode())
    print(f'Inserted commit {commit} into {filepath}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
