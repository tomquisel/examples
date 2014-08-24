#!/usr/bin/env python

def main():
    print "getAllPermsMap(3):"
    print getAllPermsMap(3)
    print "getAllPermsRec(3):"
    print getAllPermsRec(3)

def getAllPermsMap(num):
    nperms = 1
    for i in range(1,num+1):
        nperms *= i
    perms = []
    for i in range(nperms):
        perms.append(mapPerm(i, num))
    return perms

def mapPerm(x, c):
    perm = []
    locMap = {}
    for i in range(c):
        pos = x % (i + 1)
        locMap[i] = pos
        x -= pos
        x /= (i+1)
    # locmap will look like { 0:0, 1:1, 2:0 }
    for v,pos in locMap.iteritems():
        if pos == len(perm):
            perm.append(v)
            continue
        perm[pos+1:] = perm[pos:]
        perm[pos] = v
    return perm

def getAllPermsRec(num):
    if num == 0:
        return [[]]
    nm1perms = getAllPermsRec(num - 1)
    nperms = []
    for perm in nm1perms:
        for pos in range(num):
            permCopy = list(perm)
            if pos == len(perm):
                permCopy.append(num - 1)
            else:
                permCopy[pos+1:] = permCopy[pos:]
                permCopy[pos] = num - 1
            nperms.append(permCopy)
    return nperms

if __name__ == '__main__':
    main()
