def solve(X, Y, solution):
    if not X:
        yield list(solution)
    else:
        c = min(X, key=lambda c: len(X[c]))
        for r in list(X[c]):
            solution.append(r)
            cols = select(X, Y, r)
            for s in solve(X, Y, solution):
                yield s
            deselect(X, Y, r, cols)
            solution.pop()

def select(X, Y, r):
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].remove(i)
        cols.append(X.pop(j))
    return cols

def deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)



def main():
    X = {1, 2, 3, 4, 5, 6, 7}
    Y = {
        1: [1, 4, 7],
        2: [1, 4],
        3: [4, 5, 7],
        4: [3, 5, 6],
        5: [2, 3, 6, 7],
        6: [2, 7]}

    X = {j: set(filter(lambda i: j in Y[i], Y)) for j in X}

    solution = []
    a = solve(X, Y, solution)
    for i in a:
        print(i)

if __name__ == "__main__":
    main()