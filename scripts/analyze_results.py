#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

# Clean, simple plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

PALETTE = {
    'BubbleSortPassPerItem': '#E66101',
    'BubbleSortUntilNoChange': '#5E3C99',
    'BubbleSortWhileNeeded': '#2CA25F'
}

ALG_NAMES = {
    'BubbleSortPassPerItem': 'PassPerItem',
    'BubbleSortUntilNoChange': 'UntilNoChange',
    'BubbleSortWhileNeeded': 'WhileNeeded'
}

def load_data():
    return pd.read_csv("results/raw_measurements.csv")

def compute_stats(df):
    # Compute 5-number summary, mean, std, and 95% CI
    def get_summary(s):
        n = len(s)
        mean = s.mean()
        std = s.std(ddof=1)
        se = std / np.sqrt(n)
        ci_half = 2.045 * se # t-crit for df=29
        return pd.Series({
            'N': n,
            'Mean': mean,
            'StdDev': std,
            'CI95_Low': mean - ci_half,
            'CI95_High': mean + ci_half,
            'Min': s.min(),
            'Q1': s.quantile(0.25),
            'Median': s.median(),
            'Q3': s.quantile(0.75),
            'Max': s.max()
        })

    summary = df.groupby(['algorithm', 'distribution', 'array_size', 'data_type'])['execution_time_ms'].apply(get_summary).unstack().reset_index()
    summary.to_csv("results/descriptive_statistics.csv", index=False)
    return summary

def plot_design_diagram():
    # Figure for Section 2.2: Field & Hole style factorial design
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=300)
    ax.axis('off')

    ax.text(0.5, 0.93, "Experimental Design: Full Factorial (3 × 4 × 5 × 2)",
            ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.85, "120 unique conditions, 30 repetitions each = 3,600 total runs",
            ha='center', va='center', fontsize=9, color='#555555')

    factors = [
        {"title": "Factor 1: Algorithm\n(3 levels)", "items": ["PassPerItem", "UntilNoChange", "WhileNeeded"], "color": "#EBF3FB", "border": "#3182BD"},
        {"title": "Factor 2: Distribution\n(4 levels)", "items": ["Random", "Sorted", "Reverse", "Nearly (95%)"], "color": "#EAF7EB", "border": "#31A354"},
        {"title": "Factor 3: Size (N)\n(5 levels)", "items": ["100", "500", "1,000", "2,500", "5,000"], "color": "#FDF2E9", "border": "#E6550D"},
        {"title": "Factor 4: Data Type\n(2 levels)", "items": ["Integer", "String"], "color": "#F4ECF7", "border": "#756BB1"}
    ]

    xs = [0.12, 0.37, 0.62, 0.87]
    for f, x in zip(factors, xs):
        box = FancyBboxPatch((x - 0.1, 0.63), 0.2, 0.16, boxstyle="round,pad=0.01", facecolor=f["color"], edgecolor=f["border"], linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, 0.71, f["title"], ha='center', va='center', fontsize=8.5, fontweight='bold')

        y = 0.55
        for item in f["items"]:
            lvl = FancyBboxPatch((x - 0.09, y - 0.025), 0.18, 0.05, boxstyle="round,pad=0.01", facecolor="white", edgecolor=f["border"], linewidth=0.8, linestyle="--")
            ax.add_patch(lvl)
            ax.text(x, y, item, ha='center', va='center', fontsize=8)
            y -= 0.065

    # Bottom connection box
    bot = FancyBboxPatch((0.08, 0.06), 0.84, 0.12, boxstyle="round,pad=0.01", facecolor="#F8F9FA", edgecolor="#666666", linewidth=1.2)
    ax.add_patch(bot)
    ax.text(0.5, 0.13, "Repeated Measures with Randomized Trial Order", ha='center', va='center', fontsize=9, fontweight='bold')
    ax.text(0.5, 0.08, "Dependent Variable: Execution Time in ms (measured via System.nanoTime())", ha='center', va='center', fontsize=8, color="#005A32")

    plt.tight_layout()
    # Save as backup without overwriting the hand-drawn figure 1
    plt.savefig("figures/fig1_generated_design_backup.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_boxplots(df):
    # Figure for Section 3.1: Visual Overview
    sub = df[(df['array_size'] == 2500) & (df['data_type'] == 'Integer')].copy()
    sub['alg_short'] = sub['algorithm'].map(ALG_NAMES)

    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), dpi=300, sharey=False)
    dists = ['RANDOM', 'NEARLY_SORTED', 'REVERSE_SORTED', 'SORTED']
    titles = ['(a) Random', '(b) Nearly Sorted (95%)', '(c) Reverse Sorted', '(d) Sorted']

    order = ['PassPerItem', 'UntilNoChange', 'WhileNeeded']
    colors = [PALETTE['BubbleSortPassPerItem'], PALETTE['BubbleSortUntilNoChange'], PALETTE['BubbleSortWhileNeeded']]

    for ax, dist, title in zip(axes, dists, titles):
        data = sub[sub['distribution'] == dist]
        sns.boxplot(data=data, x='alg_short', y='execution_time_ms', hue='alg_short', order=order, palette=colors, ax=ax, width=0.45, fliersize=3, legend=False)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlabel("")
        ax.set_ylabel("Time (ms)" if ax == axes[0] else "", fontsize=9)
        ax.tick_params(axis='x', rotation=0, labelsize=7.5)
        ax.tick_params(axis='y', labelsize=8)

    plt.suptitle("Execution Times by Algorithm (N = 2,500 Integers, 30 Runs)", fontsize=11, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig("figures/fig2_boxplot_distributions.png", dpi=300, bbox_inches='tight')
    plt.savefig("figures/fig2_boxplot_distributions.pdf", bbox_inches='tight')
    plt.savefig("report/figures/fig2_boxplot_distributions.pdf", bbox_inches='tight')
    plt.close()

def main():
    df = load_data()
    compute_stats(df)
    plot_boxplots(df)
    print("Generated descriptive statistics and Figure 2 boxplots.")

if __name__ == "__main__":
    main()
