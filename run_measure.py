# run_measure.py

from __future__ import annotations
import argparse, os, time, math, statistics, json, random
import pandas as pd
import matplotlib.pyplot as plt

from src.deck import create_deck
from src.algorithms import (
    las_vegas_equity, monte_carlo_equity,            # bestehend (Heads-Up, Preflop)
    las_vegas_equity_known_board, monte_carlo_equity_known_board,  # NEU (Heads-Up, known board)
    las_vegas_equity_multi, monte_carlo_equity_multi,              # NEU (Multi, Preflop)
    las_vegas_equity_multi_known_board, monte_carlo_equity_multi_known_board  # NEU (Multi, known board)
)

def ensure_results():
    os.makedirs("results", exist_ok=True)

def mean_ci(values):
    m = statistics.mean(values)
    if len(values) < 2:
        return m, m, m
    s = statistics.stdev(values)
    half = 1.96 * s / math.sqrt(len(values))
    return m, m - half, m + half

def plot_hist(data, title, outpng):
    plt.figure()
    plt.hist(data, bins=20)
    plt.title(title)
    plt.xlabel("Equity-Schätzung")
    plt.ylabel("Häufigkeit")
    plt.tight_layout()
    plt.savefig(outpng, dpi=200)
    plt.close()

def plot_convergence(xs, ys, exact, title, outpng):
    plt.figure()
    plt.plot(xs, ys)
    if exact is not None:
        plt.axhline(y=exact, linestyle="--")
    plt.title(title); plt.xlabel("Anzahl Simulationen"); plt.ylabel("Equity")
    plt.tight_layout(); plt.savefig(outpng, dpi=200); plt.close()

# --- Szenarien ---
def scenario_S1():
    # Heads-Up, Preflop
    hero = ["AS","KS"]
    villain = ["QD","QC"]
    board_known = []
    tag = "S1_AKs_vs_QQ_preflop"
    return hero, [villain], board_known, tag

def scenario_S2():
    # 3-Player, Preflop
    hero = ["AS","KS"]
    villains = [["QD","QC"], ["7C","8C"]]
    board_known = []
    tag = "S2_AKs_vs_QQ_vs_78c_preflop"
    return hero, villains, board_known, tag

def scenario_S3():
    # Heads-Up, Flop bekannt
    hero = ["AS","KS"]
    villain = ["QH","QD"]
    board_known = ["QH","2S","9D"]
    tag = "S3_postflop_known_flop"
    return hero, [villain], board_known, tag

def run():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--mc", type=int, default=100_000)
    ap.add_argument("--conv", type=int, default=50_000)
    ap.add_argument("--conv_step", type=int, default=2_000)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    ensure_results()
    deck = create_deck()

    # ---------- S1: Heads-Up Preflop ----------
    hero, villains, board_known, tag = scenario_S1()
    t0 = time.perf_counter(); exact = las_vegas_equity(hero, villains[0], deck); t1 = time.perf_counter()
    exact_info = {"equity": exact, "time_s": t1 - t0}
    with open(f"results/{tag}_exact.json","w") as f: json.dump(exact_info, f, indent=2)

    ests, times = [], []
    for i in range(args.runs):
        if args.seed is not None:
            random.seed(args.seed + i)
        t0 = time.perf_counter()
        p = monte_carlo_equity(hero, villains[0], deck, iterations=args.mc)
        times.append(time.perf_counter() - t0); ests.append(p)
    m, lo, hi = mean_ci(ests)
    pd.DataFrame({"estimate": ests, "time_s": times}).to_csv(f"results/{tag}_mc_runs.csv", index=False)
    plot_hist(ests, f"{tag}: MC (N={args.mc}, runs={args.runs})", f"results/{tag}_mc_hist.png")

    # Konvergenz (ein Durchlauf inkrementell)
    xs, ys = [], []
    wins_share = 0.0
    for n in range(1, args.conv + 1):
        p = monte_carlo_equity(hero, villains[0], deck, iterations=1)  # 1 Stichprobe
        wins_share += p
        if n % args.conv_step == 0:
            xs.append(n); ys.append(wins_share / n)
    plot_convergence(xs, ys, exact, f"{tag}: Konvergenz", f"results/{tag}_mc_convergence.png")

    # ---------- S2: 3-Player Preflop ----------
    hero2, villains2, board_known2, tag2 = scenario_S2()
    t0 = time.perf_counter(); exact2 = las_vegas_equity_multi(hero2, villains2, deck); t1 = time.perf_counter()
    with open(f"results/{tag2}_exact.json","w") as f: json.dump({"equity": exact2, "time_s": t1-t0}, f, indent=2)

    ests2, times2 = [], []
    for i in range(args.runs):
        if args.seed is not None:
            random.seed(args.seed + 1000 + i)
        t0 = time.perf_counter()
        p = monte_carlo_equity_multi(hero2, villains2, deck, iterations=args.mc)
        times2.append(time.perf_counter() - t0); ests2.append(p)
    m2, lo2, hi2 = mean_ci(ests2)
    pd.DataFrame({"estimate": ests2, "time_s": times2}).to_csv(f"results/{tag2}_mc_runs.csv", index=False)
    plot_hist(ests2, f"{tag2}: MC (N={args.mc}, runs={args.runs})", f"results/{tag2}_mc_hist.png")

    # ---------- S3: Heads-Up, Flop bekannt ----------
    hero3, villains3, board_known3, tag3 = scenario_S3()
    t0 = time.perf_counter(); exact3 = las_vegas_equity_known_board(hero3, villains3[0], deck, board_known3); t1 = time.perf_counter()
    with open(f"results/{tag3}_exact.json","w") as f: json.dump({"equity": exact3, "time_s": t1-t0}, f, indent=2)

    ests3, times3 = [], []
    for i in range(args.runs):
        if args.seed is not None:
            random.seed(args.seed + 2000 + i)
        t0 = time.perf_counter()
        p = monte_carlo_equity_known_board(hero3, villains3[0], deck, board_known3, iterations=args.mc)
        times3.append(time.perf_counter() - t0); ests3.append(p)
    m3, lo3, hi3 = mean_ci(ests3)
    pd.DataFrame({"estimate": ests3, "time_s": times3}).to_csv(f"results/{tag3}_mc_runs.csv", index=False)
    plot_hist(ests3, f"{tag3}: MC (N={args.mc}, runs={args.runs})", f"results/{tag3}_mc_hist.png")

    # Zusammenfassung
    summary = pd.DataFrame({
        "scenario":   [tag,        tag2,        tag3],
        "exact_eq":   [exact,      exact2,      exact3],
        "mc_mean":    [m,          m2,          m3],
        "mc_ci_low":  [lo,         lo2,         lo3],
        "mc_ci_high": [hi,         hi2,         hi3]
    })
    summary.to_csv("results/summary.csv", index=False)
    print(summary.to_string(index=False))

if __name__ == "__main__":
    run()
