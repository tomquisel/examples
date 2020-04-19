import argparse
from collections import deque


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    print(simplify_path(args.path))


def simplify_path(path):
    #  In a path containing an arbitrary number of "/.." parts, like
    #  "/a/b/c/d/../../e" implement an algorithm that removes all instances of /..
    #  along with the preceding directory, to reduce away all /.. syntactically.
    parts = path.split("/")
    llist = deque()
    for p in parts:
        if p == ".." and len(llist) > 1:
            llist.pop()
        else:
            llist.append(p)
    return "/".join(list(llist))


def simplify_path_map_reduce(path):
    pass


main()
