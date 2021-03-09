import numpy as np
import pytest


# ~~!~~ TESTS ~~!~~

def test_rime_equation(n_time, n_chan, n_dir, load_data):    

    (tbin_indices, tbin_counts, ant1, ant2,
            clean_vis, _, model, weight, jones) = load_data

    for t in range(n_time):
        start = tbin_indices[t]
        end = tbin_indices[t] + tbin_counts[t]
        for row in range(start, end):
            p = ant1[row]
            q = ant2[row]
            sqrtW = np.sqrt(weight[row])
            for nu in range(n_chan):
                LHS = sqrtW * clean_vis[row, nu]
                RHS = 0.0 + 0.0j
                for s in range(n_dir):
                    g_p = jones[t, p, nu, s, 0]
                    M_pq = model[row, nu, s]
                    g_q = jones[t, q, nu, s, 0]
                    RHS += sqrtW * g_p * M_pq\
                            * g_q.conjugate()
                
                assert LHS == RHS