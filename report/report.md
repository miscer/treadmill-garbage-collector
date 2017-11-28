---
title: CS4201 Practical 2
date: 29 November 2017
author: 140015533
toc: true
---

* num_free is updated when free or bottom is updated
* i found that it is difficult and error-prone to construct a test heap for each corner case in the collector - especially since it is incremental
* floating garbage

# Introduction

The reference for my implementation is from the book Garbage Collection by Jones and Lins. In the book the meanings of the colours ecru (or off-white) and white are switched - ecru is used for free cells and white is used for unscanned cells. In this report and in my implementation these definitions are used, instead of the ones used by Baker in his paper.

# Design and implementation

## Episcopal runtime objects

The implementations of Episcopal and the treadmill collector are separate. All Episcopal runtime objects are implemented as classes with one common superclass - `RuntimeObject`.

`RuntimeObject` contains the `children` method which has to return a list of cells where the child objects are stored. The default implementation returns an empty tuple, meaning that it has no children.

If an object has children, it needs to override the method. For example, the `DISTRIB` object has a number of children:

- `d` is an identifier
- `n` is an integer
- `p1` to `pn` are elements

## Memory API

The API for the garbage collector is exposed through the `Heap` class.

This class takes multiple parameters in its constructor:

- `get_roots` is a function that returns a list of root cells
- `get_children` is a function that given a value inside a cell, returns a list of child cells
- `initial_size` is the number of initial cells that are created in the heap
- `scan_step_size` defines how many cells are scanned on each allocation
- `expand_size` is how many cells are added when the garbage collector has not enough memory to satisfy an allocation request
- `scan_threshold` defines when scanning should start, as a ratio of free cells and all cells

Mutators must implement the `get_roots` and `get_children` functions. For example, `get_roots` can take the values of all registers and the values on the stack. For pointers, `get_children` can return the cell the pointer is pointing to. Episcopal implements the `get_children` function by simply calling the `children` method on the runtime object stored in the cell.

Allocation is done through the `allocate` method, which takes no arguments and returns an empty cell.

Reading from and writing to cells is implemented using the `read` and `write` methods. Both methods take a cell to read/write, `read` returns the value inside cell, `write` takes the value to be written as a parameter.

## Collector cells

The collector provides cells for the mutator. Each cell can hold any value of any size.

This way I did not have to worry about different sizes of runtime objects. If I were implementing the algorithm in a language without its own garbage collector, I would need to find a solution for different-size cells. However, since Baker's paper does not deal with these and the purpose of this practical is to implement the core idea of the treadmill algorithm, I chose the language so that I would not need to deal with these.

In addition to the value, the cells hold some additional metadata. First is the mark, used to differentiate between white and black/grey cells during scanning. In my implementation this is a boolean, since the algorithm needs only 1 bit to store the colour of a cell.

The other two are pointers to the previous and next cell in the linked list.

## Cyclic doubly-linked list

A doubly-linked list has two pointers in each element - to the previous and the next element. A cyclic doubly-linked list does not have a first or last element - elements are linked in a cycle.

In my implementation the collector cells are elements in the list. I implemented some functions for working with these lists:

- `initialize` will make a list with one element
- `insert_between`, `insert_before` and `insert_after` insert elements into the list, updating the pointers of surrounding elements as needed
- `remove` removes an element from the list and updates pointers
- `iterate` iterates through all elements in the list, starting from the passed element

## Initial cells

When the heap is constructed, a number of initial free cells are allocated. However, if this is not desired, the number of initial cells can be reduced to 1 by setting the `initial_size` parameter. This one cell is required to be able to initialise the `free` pointer, which has to be set at all times.

## Pointers

The treadmill collector uses 4 pointers to cells: `top`, `bottom`, `free` and `scan`. In the paper these point "between" cells, but my implementation the pointers point to cells. This means that I had to make rules about how the pointers should work:

## Allocation

Allocation is very simple with the treadmill collector - it simply moves the `free` pointer to the next cell and returns the cell `free` pointed to originally.

I implemented allocation as the `allocated` method in `Heap`. Besides modifying the `free` pointer, it also checks if there are other allocated cells (and the `bottom` pointer is set). If not, it sets `bottom` to the allocated cell, essentially painting it black.

Before the cell is allocated, three things are checked:

1. If there is less free cells than `scan_threshold` allows, scanning will start
2. If scanning is in progress, some cells should be scanned
3. If there is only one free cell left, the heap should be expanded

The newly allocated cell is guaranteed to be black, since all of these operations run before the `free` pointer is modified.

## Triggering scanning

The collector needs to start scanning when it thinks it might run out of free cells before scanning is finished. If the mutator allocates cells faster than the collector can deallocate, the heap needs to be expanded, as described below.

In this implementation the heuristic for determining the ideal time to start scanning is fairly simple - a threshold ratio of free and total cells can be set. If this threshold is passed, for example 20% of all cells are free, the collector will start scanning.

This could be improved by having the collector observe the mutator's behaviour - for instance, if it's allocating often and generates a lot of garbage, scanning should begin early to avoid having to expand the heap.

## Starting scanning

## Scan cycle and step

## Collecting

## Expanding

If the collector runs out of free cells, it needs to create more of them. The program simply does this when it is about to allocate the last free cell.

A number of free cells is first created. This number can be configured by the mutator using the `expand_size` parameter. These cells are then inserted after the last free cell.

These additional cells are never released, even if the mutator's memory requirements become lower after some time. To improve this, the collector could monitor the number of free cells and if it stays too high for some time, it could release some of them.

## Statistics

As the collector allocates and frees cells, it maintains the number of free, scanned and total cells - `num_free`, `num_scanned`, `num_total`.

`num_total` is initialised when the heap is constructed, and is incremented when the heap is expanded.

`num_scanned` is reset to 0 when scanning starts, and is incremented by 1 for each scanned cell.

`num_free` is a little trickier to maintain without iterating through the whole heap and counting the free cells. It is initialised to `num_total` when heap is constructed and decremented by 1 each time a cell is allocated. When the heap is expanded, `num_free` is incremented by the number of new cells. Finally, when scanning is finished and garbage is collected, `num_free` is set to `num_total - num_scanned`. This works because we always know the exact value of `num_total`, and we also know the number of cells that are live (`num_scanned`). At collection, all cells that were not scanned (i.e. are not live) are garbage and therefore free.

The number of total and free cells are then used to know when to start scanning the heap and collecting garbage.

## Read barrier

Since the treadmill collector is incremental, we need to make sure that the mutator does not cause inconsistencies during scanning by modifying the runtime objects.

Baker suggests to use a read barrier that will make sure the mutator never sees a white (unscanned) object, only a grey or black (scanned) one.

When the mutator wishes to modify an object, it needs to read it first. If it attempts to read an unscanned object, the collector will mark it to be scanned (i.e. paint it grey). If it reads an already scanned or marked to be scanned object, no action is needed.

Checking whether a cell is unscanned or marked to be scanned is implemented using the `mark` attribute of each cell. The heap has a `live_mark` attribute that contains either `True` or `False`, as described below. If `cell.mark == heap.live_mark`, then the cell has already been scanned or is marked to be scanned.

# Testing

## Unit testing

I found that it is difficult and error-prone to construct a test heap for each corner case in the collector - especially since it is incremental. Therefore I opted for using unit tests to make sure the collector works properly, in addition to constructing test heaps.

Each method in the `Heap` class and all functions for manipulating linked lists are covered by unit tests, so I can be certain that my implementation will work as expected.

Every unit test constructs a specific heap by directly modifying the pointers, live mark and statistics. Since these are the only state the heap holds, we can modify them as we need and the heap will act as if some operations were carried out.

For example, to check if the collector expands the heap when it runs out of free cells, we initialise a heap with 10 initial free cells and modify the state:

* `free` is set to the last free cell
* `bottom` is set to the first free cell
* `num_free` is set to 1

This is the same state that would occur after the collector allocated all but one free cell and did not do any garbage collection or scanning.

## Test heaps

To put the collector into a real-world scenario, I decided to try to implement a basic linked list using Episcopal objects. I used `IND` objects that point from one to another to form a linked list, with the last one not pointing to any cell (a null pointer).

Then I declared to the collector the first pointer in the list as a root. The collector should be able to find all other elements of the list by scanning the children of the indirection objects.

I create a list of 100 elements ten times, discarding the existing list before the new one is constructed. This way the collector should allocate enough free cells to hold one linked list, plus a few leftover objects from the previous list.

When we run `linked_list.py`, the output is:

```
10 free out of 10 total, 0 scanned
9 free out of 110 total, 0 scanned
33 free out of 130 total, 19 scanned
30 free out of 130 total, 7 scanned
29 free out of 130 total, 4 scanned
29 free out of 130 total, 3 scanned
29 free out of 130 total, 3 scanned
29 free out of 130 total, 3 scanned
29 free out of 130 total, 3 scanned
29 free out of 130 total, 3 scanned
29 free out of 130 total, 3 scanned
```

We can see that the total number of cells becomes 130, meaning that the collector could not keep up with the memory requirements of the mutator, but eventually expanded the heap to a size where it could. A stable number of total cells also means that there is no leftover garbage that did not get collected.

## Stress testing

One of my testing techniques was a form of stress testing. In this test the program will continuously allocate 2000 cells and keep 100 of them as roots. After each allocation, it will check that the allocated cell is not one of the roots.

This way I was able to find many corner cases and bugs in my program before the implementation was fully finished and I could write a complete unit test suite.

The stress test is in `stress_test.py`.

## Coverage

I used coverage.py^[https://coverage.readthedocs.io/en/coverage-4.4.2/] to check that the unit tests cover all the code. This tool simply runs a Python program and monitors which statements were executed. When we run all unit tests, the coverage report will show any statements that were not executed during unit tests and therefore are not tested.

My unit tests cover all functions in `heap.py` and `list.py`, meaning that I have tested for all corner possible executions through the code. The coverage report for those two files is in the submission.

# Evaluation

# Extensions

Baker's treadmill algorithm, as described in the paper, only collects garbage once there are no free cells left. In my implementation the garbage is collected as soon as scanning is finished.

On its own this does not bring any improvements, but if it were paired with the collector releasing memory held by free cells if they are not needed, it could result in better memory utilisation. The memory could be released right after scanning is finished, instead of waiting for all free cells to get allocated as Baker describes it.
