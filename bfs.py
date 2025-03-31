from collections import deque

queue = deque()
nodes = dict()
checked = set()

nedges = input("Enter the amount of edges: ")

for i in range(int(nedges)):

    src = input("Enter the source node: ")
    des = input("Enter the destination node: ")
    if (src) not in nodes:
        temp = [des]
        nodes.update({src: temp})
    else:
        nodes[src].append(des)

npaths = input("Enter the amount of paths to be checked: ")

for i in range(int(npaths)):

    src = input("Enter the source node: ")
    des = input("Enter the destination node: ")

    queue.append(src)

    while len(queue) > 0:

        target = queue.popleft()

        if target in checked:
            continue

        if target == des:
            path = 1

        checked.add(target)

        if target in nodes:
                queue.extend(nodes[target])

    if path == 1:
        print("There is a path between", src, "and", des)
    else:
        print("There is not a path between", src, "and", des)

    path = 0
    checked.clear()











