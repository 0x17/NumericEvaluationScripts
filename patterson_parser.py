import sys
import json


def to_int(l): return [int(v) for v in l]


def col(mx, ix): return [row[ix] for row in mx]


def matrix_sum(mx):
    return sum(mx[i][j] for i in range(len(mx)) for j in range(len(mx[0])))

#TODO
def compute_ess(adj_mx, durations):
    return []

#TODO
def peak_demand(sts, demands, r):
    return 0


def complexity_measures(adj_mx, demands, capacities, durations):
    njobs = len(adj_mx)
    nres = len(demands[0])
    assert (njobs == len(demands))
    nc = matrix_sum(adj_mx) / njobs
    rf = 1 / (njobs * nres) * sum(1 if demands[j][r] > 0 else 0 for r in range(nres) for j in range(njobs))
    ess = compute_ess(adj_mx, durations)
    rsvec = [(capacities[r] - max(col(demands, r))) / (peak_demand(ess, demands, r) - max(col(demands, r))) for r in range(nres)]
    rs = sum(rsvec) / len(rsvec)
    return dict(nc=nc, rf=rf)


def parse(filename):
    with open(filename, 'r') as fp:
        lines = fp.readlines()
        grid = [to_int(line.split()) for line in lines if len(line.strip()) > 0]
        njobs, nres = grid[0]
        capacities = grid[1]
        durations = col(grid[2:], 0)
        demands = [col(grid[2:], 1 + res) for res in range(nres)]
        adj_mx = [[1 if j in grid[2 + i][6:] else 0 for j in range(njobs)] for i in range(njobs)]
        cm = complexity_measures(adj_mx, demands, capacities, durations)
        return dict(njobs=njobs, nres=nres, capacities=capacities, durations=durations, demands=demands, adj_mx=adj_mx, complexity_measures=cm)


if __name__ == '__main__':
    if len(sys.argv) >= 2 and '.rcp' in sys.argv[1]:
        with open(sys.argv[1].split('.')[0] + '.json', 'w') as fp:
            json.dump(parse(sys.argv[1]), fp)
