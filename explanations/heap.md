# A heap

A heap (we'll discuss a min heap) is a data structure designed to make finding & removing the smallest (or largest) element fast. Specifically, it is a tree where each parent is not greater than all its children. It implements a priority queue. It's also used in the heap sort algorithm, which constructs a heap of the values, and then repeatedly runs `popmin()` to extract the sorted list.

There are many kinds of heap data structures. A binary heap is the simplest, while a Fibonacci heap has the best algorithm complexity across common operations.

## Algorithmic complexity

For a binary heap:

|find-min|delete-min|insert|decrease-key|meld|
|-|-|-|-|-|
| O(1) | O(log n) | O(log n) |  O(log n) | O(n) |
