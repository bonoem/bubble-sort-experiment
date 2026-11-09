#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "  USI Experimentation & Evaluation 2026 - Experiment 01 Reproduction Pipeline  "
echo "==============================================================================="
echo ""

# 1. Compile Java source files
echo "Step 1: Compiling Java benchmark infrastructure..."
javac -d . Sorter.java BubbleSortPassPerItem.java BubbleSortUntilNoChange.java BubbleSortWhileNeeded.java exp01/BenchmarkRunner.java

# 2. Run Java Benchmark
echo ""
echo "Step 2: Executing full factorial randomized benchmark harness..."
java -Xms2g -Xmx2g -cp . exp01.BenchmarkRunner

# 3. Analyze data and generate plots
echo ""
echo "Step 3: Generating descriptive statistics and publication-quality figures..."
python3 scripts/analyze_results.py

# 4. Compile PDF report
echo ""
echo "Step 4: Compiling LaTeX report to PDF..."
cd report
pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1 || pdflatex -interaction=nonstopmode report.tex
pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1
cd ..

echo ""
echo "==============================================================================="
echo "  Reproduction pipeline completed successfully!                                "
echo "  Raw data: results/raw_measurements.csv                                       "
echo "  Summary:  results/descriptive_statistics.csv                                 "
echo "  Report:   report/report.pdf                                                  "
echo "==============================================================================="
