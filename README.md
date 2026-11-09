# Assignment 1: The Bubble Algorithm Library
**Course:** Experimentation & Evaluation 2026  
**Instructors:** Prof. Gabriele Bavota, Giuseppe Crupi  
**Institution:** Università della Svizzera italiana (USI), Faculty of Informatics  
**Student:** Emanuele Bono  

---

## Executive Summary & Recommendation
Bubble Inc. tasked us with recommending the most suitable bubble sort implementation for their production Java utility library among three candidate algorithms:
1. `BubbleSortPassPerItem` (Baseline: unconditional $N \times (N-1)$ comparisons)
2. `BubbleSortUntilNoChange` (Early exit flag: terminates if no swaps occur during a pass)
3. `BubbleSortWhileNeeded` (Dynamic boundary tracking: resets pass upper bound to the index of the last swap)

### Recommendation:
> **Adopt `BubbleSortWhileNeeded` for the production library.**

### Key Findings:
- **Strict Dominance:** `BubbleSortWhileNeeded` strictly outperforms or matches the other two candidate algorithms across all 120 experimental conditions ($3 \text{ algorithms} \times 4 \text{ distributions} \times 5 \text{ sizes} \times 2 \text{ data types}$).
- **Average-Case Speedup:** On random arrays ($N=5,000$), `WhileNeeded` achieves a **30.6% speedup** on Integers (39.98 ms vs. 57.65 ms) and a **39.3% speedup** on Strings (74.57 ms vs. 122.82 ms).
- **Best-Case Linear Acceleration:** On pre-sorted inputs ($N=5,000$), both `UntilNoChange` and `WhileNeeded` achieve linear $O(N)$ execution, sorting in **0.009 ms (over 3,500x faster than the 32.18 ms required by `PassPerItem`)**.
- **The Inefficiency Trap of `UntilNoChange`:** `BubbleSortUntilNoChange` performs virtually identically to the unoptimized baseline on random, nearly sorted, and reverse sorted arrays because it lacks boundary contraction. In contrast, `WhileNeeded` contracts the boundary on every single pass.

---

## Repository Structure

```
assignment 1/
├── README.md                          # Project documentation and summary
├── Sorter.java                        # Generic Sorter interface
├── BubbleSortPassPerItem.java         # Baseline implementation
├── BubbleSortUntilNoChange.java       # Early stopping implementation
├── BubbleSortWhileNeeded.java         # Dynamic bound contraction implementation
├── exp01/                             # Java package directory
│   ├── Sorter.java
│   ├── BubbleSortPassPerItem.java
│   ├── BubbleSortUntilNoChange.java
│   ├── BubbleSortWhileNeeded.java
│   └── BenchmarkRunner.java           # Multi-factor experimental benchmark harness
├── results/
│   ├── raw_measurements.csv           # Complete dataset: 3,600 trial observations
│   ├── descriptive_statistics.csv     # 5-number summary, means, std dev, 95% CIs
│   ├── summary_table.md               # Markdown summary table
│   └── summary_table.tex              # LaTeX summary table
├── figures/
│   ├── fig1_experimental_design.png   # Field & Hole style factorial design diagram
│   ├── fig2_boxplot_distributions.png # Performance distributions across workloads
│   ├── fig3_scaling_curves.png        # Scaling curves with 95% confidence bands
│   ├── fig4_datatype_comparison.png   # Integer vs. String performance comparison
│   └── fig5_log_scale_overview.png    # Logarithmic scaling overview
├── scripts/
│   ├── run_benchmark.sh               # One-command full reproduction pipeline
│   └── analyze_results.py             # Python statistics and visualization pipeline
└── report/
    ├── report.pdf                     # Formal compiled PDF experiment report
    ├── report.tex                     # LaTeX source matching USI course template
    └── report.md                      # Markdown report for Google Docs copy/paste
```

---

## One-Command Reproduction Pipeline

To replicate the entire experiment from scratch, execute:

```bash
bash scripts/run_benchmark.sh
```

This single command:
1. Compiles all Java classes (`javac -d . *.java`).
2. Executes 3,600 experimental trials across 120 factor combinations under fixed JVM heap (`-Xms2g -Xmx2g`).
3. Computes complete descriptive statistics (5-number summary, means, standard deviations, and 95% confidence intervals).
4. Generates high-resolution figures (PNG and PDF vector format).
5. Compiles the formal LaTeX report to PDF (`report/report.pdf`).

---

## Hardware and Software Environment
- **Machine:** Apple MacBook Pro (Apple M3 Pro SoC, 11 CPU cores, 18 GB RAM)
- **OS:** macOS Darwin Kernel Version 25.5.0
- **Java Runtime:** Eclipse Adoptium OpenJDK 25.0.2 LTS (build 25.0.2+10-LTS)
- **Python:** Python 3.12 (NumPy, Pandas, SciPy, Matplotlib, Seaborn)
- **LaTeX:** TeX Live 2024 / pdfTeX 3.141592653
