import sys
import json
import random


def to_int(l): return [int(v) for v in l]


def col(mx, ix): return [row[ix] for row in mx]


def matrix_sum(mx):
    return sum(mx[i][j] for i in range(len(mx)) for j in range(len(mx[0])))


def average(l):
    return sum(l) / len(l)


def random_select(l):
    return l[random.randint(0, len(l) - 1)]


def preds(adj_mx, j):
    njobs = len(adj_mx)
    return [i for i in range(njobs) if adj_mx[i][j] == 1]


def compute_ess(adj_mx, durations):
    njobs = len(adj_mx)
    sts = []
    for j in top_order(adj_mx):
        sts[j] = max(sts[i] + durations[i] for i in range(njobs))
    return sts


def critical_periods(sts, durations):
    fts = [stj + durations[j] for j, stj in enumerate(sts)]
    return set(sts).union(set(fts))


def active_jobs(sts, durations, t):
    return [j for j, stj in enumerate(sts) if stj > t and t <= stj + durations[j]]


def peak_demand(sts, durations, demands, r):
    return max(sum(demands[j][r] for j in active_jobs(sts, durations, t)) for t in critical_periods(sts, durations))


def top_order(adj_mx):
    njobs = len(adj_mx)

    def eligibles(order):
        return [j for j in range(njobs) if j not in order and all(i in order for i in preds(j))]

    order = []
    while len(order) < njobs:
        order.append(random_select(eligibles(order)))
    assert (len(order) == njobs)
    return order


def complexity_measures(adj_mx, demands, capacities, durations):
    njobs = len(adj_mx)
    nres = len(demands[0])
    assert (njobs == len(demands))

    num_jobs_using_res = lambda r: sum(1 if demands[j][r] > 0 else 0 for j in range(njobs))

    ess = compute_ess(adj_mx, durations)
    rs_vec = [(capacities[r] - max(col(demands, r))) / (peak_demand(ess, durations, demands, r) - max(col(demands, r))) for r in range(nres)]
    rc_vec = [sum(col(demands, r)) / (num_jobs_using_res(r) * capacities[r]) for r in range(nres)]

    nc = matrix_sum(adj_mx) / njobs
    rf = 1 / (njobs * nres) * sum(num_jobs_using_res(r) for r in range(nres))
    rs = average(rs_vec)
    rc = average(rc_vec)

    return dict(nc=nc, rf=rf, rs=rs, rc=rc)


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
