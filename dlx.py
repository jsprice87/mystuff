"""
Algorithm X with Dancing Links (DLX) - flat-array implementation.

This is a high-performance pure-Python implementation of Knuth's Algorithm X
using the Dancing Links technique. It uses flat arrays indexed by integer node
IDs instead of objects, which is significantly faster in Python.

Reference: Donald Knuth, "Dancing Links" (2000)
"""


class DLX:
    """Exact cover solver using Dancing Links."""

    def __init__(self, column_names):
        """Initialize with a list of column names.

        Args:
            column_names: list of strings identifying each column.
        """
        self.num_cols = len(column_names)
        self.col_name = {i + 1: name for i, name in enumerate(column_names)}
        self.name_to_col = {name: i + 1 for i, name in enumerate(column_names)}

        # Node 0 is the root header.
        # Nodes 1..num_cols are column headers.
        num_nodes = self.num_cols + 1
        self.L = list(range(-1, num_nodes - 1))  # left links
        self.R = list(range(1, num_nodes + 1))    # right links
        self.U = list(range(num_nodes))            # up links (self-loop)
        self.D = list(range(num_nodes))            # down links (self-loop)
        self.C = list(range(num_nodes))            # column header for each node
        self.S = [0] * num_nodes                   # size (count of 1s) per column
        self.ROW = [None] * num_nodes              # row identifier per node

        # Fix root header links
        self.L[0] = self.num_cols
        self.R[self.num_cols] = 0

    def add_row(self, row_id, column_names):
        """Add a row to the matrix.

        Args:
            row_id: an arbitrary identifier for this row (returned in solutions).
            column_names: list of column names that this row covers.
        """
        cols = [self.name_to_col[name] for name in column_names]
        if not cols:
            return

        first_node = None
        for col in cols:
            node = len(self.L)  # new node index
            self.L.append(0)
            self.R.append(0)
            self.U.append(self.U[col])
            self.D.append(col)
            self.C.append(col)
            self.ROW.append(row_id)

            # Insert at bottom of column
            self.U[col] = node
            self.D[self.U[node]] = node

            self.S[col] += 1

            if first_node is None:
                first_node = node
                self.L[node] = node
                self.R[node] = node
            else:
                # Insert to the right of the previous node in this row
                self.L[node] = self.L[first_node]
                self.R[node] = first_node
                self.R[self.L[first_node]] = node
                self.L[first_node] = node

    def _cover(self, col):
        """Remove column and all rows that intersect it."""
        self.R[self.L[col]] = self.R[col]
        self.L[self.R[col]] = self.L[col]
        i = self.D[col]
        while i != col:
            j = self.R[i]
            while j != i:
                self.D[self.U[j]] = self.D[j]
                self.U[self.D[j]] = self.U[j]
                self.S[self.C[j]] -= 1
                j = self.R[j]
            i = self.D[i]

    def _uncover(self, col):
        """Restore column and all rows that intersect it."""
        i = self.U[col]
        while i != col:
            j = self.L[i]
            while j != i:
                self.S[self.C[j]] += 1
                self.D[self.U[j]] = j
                self.U[self.D[j]] = j
                j = self.L[j]
            i = self.U[i]
        self.R[self.L[col]] = col
        self.L[self.R[col]] = col

    def solve(self, solution=None, callback=None):
        """Find all exact covers.

        Args:
            solution: internal use (partial solution being built).
            callback: if provided, called with each solution (list of row_ids).
                      If callback returns True, search stops early.

        Returns:
            List of solutions if no callback, else number of solutions found.
        """
        if solution is None:
            solution = []

        results = [] if callback is None else 0

        # If matrix is empty, we found a solution
        if self.R[0] == 0:
            if callback:
                if callback(list(solution)):
                    return -1  # signal to stop
                return 1
            else:
                results.append(list(solution))
                return results

        # Choose column with minimum size (S heuristic)
        min_size = float('inf')
        col = None
        j = self.R[0]
        while j != 0:
            if self.S[j] < min_size:
                min_size = self.S[j]
                col = j
                if min_size <= 1:
                    break
            j = self.R[j]

        if min_size == 0:
            return results  # dead end - uncoverable column

        self._cover(col)

        i = self.D[col]
        while i != col:
            solution.append(self.ROW[i])

            # Cover all other columns in this row
            j = self.R[i]
            while j != i:
                self._cover(self.C[j])
                j = self.R[j]

            # Recurse
            if callback:
                sub = self.solve(solution, callback)
                if sub == -1:
                    # Uncover before returning
                    j = self.L[i]
                    while j != i:
                        self._uncover(self.C[j])
                        j = self.L[j]
                    solution.pop()
                    self._uncover(col)
                    return -1
                results += sub
            else:
                sub = self.solve(solution, callback)
                results.extend(sub)

            # Uncover in reverse order
            j = self.L[i]
            while j != i:
                self._uncover(self.C[j])
                j = self.L[j]

            solution.pop()
            i = self.D[i]

        self._uncover(col)
        return results
