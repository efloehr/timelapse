from sys import argv
from pictures.models import Picture


def main(path):
    for dirpath, dirs, files in os.walk(path):
        for f in sorted(fnmatch.filter(files, '2*.jpg')):
            filepath = os.path.join(dirpath, f)
            Picture.insert.delay(filepath)


# if python says run, then we should run
if __name__ == '__main__':
    if len(argv) != 2:
        print("Please provide the directory to walk as the only argument")
    main(argv[1])
