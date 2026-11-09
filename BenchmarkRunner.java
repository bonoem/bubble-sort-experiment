package exp01;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

public final class BenchmarkRunner {

    public enum Distribution {
        RANDOM,
        SORTED,
        REVERSE_SORTED,
        NEARLY_SORTED
    }

    public static final class Trial {
        final int id;
        final int repetition;
        final String algorithmName;
        final Sorter sorter;
        final String dataType;
        final int size;
        final Distribution distribution;

        public Trial(int id, int repetition, String algorithmName, Sorter sorter,
                     String dataType, int size, Distribution distribution) {
            this.id = id;
            this.repetition = repetition;
            this.algorithmName = algorithmName;
            this.sorter = sorter;
            this.dataType = dataType;
            this.size = size;
            this.distribution = distribution;
        }
    }

    private static final int[] SIZES = {100, 500, 1000, 2500, 5000};
    private static final int REPETITIONS = 30; // 30 runs per condition
    private static final int WARMUP_RUNS = 25;
    private static final long SEED = 20261109L;

    public static void main(String[] args) {
        System.out.println("Starting sorting benchmark...");
        
        Sorter[] sorters = new Sorter[]{
                new BubbleSortPassPerItem(),
                new BubbleSortUntilNoChange(),
                new BubbleSortWhileNeeded()
        };
        String[] names = new String[]{
                "BubbleSortPassPerItem",
                "BubbleSortUntilNoChange",
                "BubbleSortWhileNeeded"
        };

        // 1. Warm up the JIT compiler
        System.out.println("Warming up JIT compiler...");
        runWarmup(sorters);

        // 2. Build the list of trials
        List<Trial> trials = new ArrayList<>();
        int id = 0;
        for (int r = 1; r <= REPETITIONS; r++) {
            for (int s : SIZES) {
                for (Distribution dist : Distribution.values()) {
                    for (String dType : new String[]{"Integer", "String"}) {
                        for (int a = 0; a < sorters.length; a++) {
                            id++;
                            trials.add(new Trial(id, r, names[a], sorters[a], dType, s, dist));
                        }
                    }
                }
            }
        }

        // Shuffle the execution order to avoid order effects
        Collections.shuffle(trials, new Random(SEED));
        System.out.println("Total trials to run: " + trials.size());

        // 3. Run measurements and save to CSV
        File outDir = new File("results");
        if (!outDir.exists()) {
            outDir.mkdirs();
        }
        File csv = new File(outDir, "raw_measurements.csv");

        long startBenchmark = System.currentTimeMillis();
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(csv))) {
            writer.write("trial_id,repetition,algorithm,data_type,array_size,distribution,execution_time_ns,execution_time_ms\n");

            int done = 0;
            for (Trial t : trials) {
                long trialSeed = SEED + ((long) t.repetition * 10007L) + ((long) t.size * 31L) + t.distribution.ordinal();
                Comparable[] base = generateArray(t.dataType, t.size, t.distribution, trialSeed);
                Comparable[] work = copyArray(base);

                // Run GC before large sizes to keep heap clean
                if (t.size >= 2500 && done % 25 == 0) {
                    System.gc();
                }

                // Measure only the sort call
                long startNs = System.nanoTime();
                t.sorter.sort(work);
                long endNs = System.nanoTime();

                long elapsedNs = endNs - startNs;
                double elapsedMs = elapsedNs / 1_000_000.0;

                // Sanity check: make sure it's actually sorted
                if (!isSorted(work)) {
                    System.err.println("Error: array not sorted by " + t.algorithmName);
                    System.exit(1);
                }

                writer.write(t.id + "," + t.repetition + "," + t.algorithmName + "," + t.dataType + "," +
                        t.size + "," + t.distribution.name() + "," + elapsedNs + "," + String.format("%.6f", elapsedMs) + "\n");

                done++;
                if (done % 600 == 0) {
                    System.out.println("Completed " + done + " / " + trials.size() + " trials...");
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        long endBenchmark = System.currentTimeMillis();
        System.out.println("Done in " + (endBenchmark - startBenchmark) / 1000.0 + " seconds.");
        System.out.println("Saved results to " + csv.getPath());
    }

    private static void runWarmup(Sorter[] sorters) {
        Random rng = new Random(42L);
        for (int w = 0; w < WARMUP_RUNS; w++) {
            for (Sorter s : sorters) {
                Integer[] intArr = new Integer[500];
                for (int i = 0; i < intArr.length; i++) intArr[i] = rng.nextInt(10000);
                s.sort(intArr);

                String[] strArr = new String[500];
                for (int i = 0; i < strArr.length; i++) strArr[i] = String.format("str_%05d", rng.nextInt(10000));
                s.sort(strArr);
            }
        }
    }

    private static Comparable[] generateArray(String dataType, int size, Distribution dist, long seed) {
        Random rng = new Random(seed);
        if ("Integer".equalsIgnoreCase(dataType)) {
            Integer[] arr = new Integer[size];
            for (int i = 0; i < size; i++) arr[i] = rng.nextInt(size * 10);
            applyDistribution(arr, dist, rng);
            return arr;
        } else {
            String[] arr = new String[size];
            for (int i = 0; i < size; i++) arr[i] = String.format("val_%05d", rng.nextInt(size * 10));
            applyDistribution(arr, dist, rng);
            return arr;
        }
    }

    @SuppressWarnings("unchecked")
    private static <T extends Comparable<T>> void applyDistribution(T[] arr, Distribution dist, Random rng) {
        int n = arr.length;
        if (dist == Distribution.SORTED) {
            java.util.Arrays.sort(arr);
        } else if (dist == Distribution.REVERSE_SORTED) {
            java.util.Arrays.sort(arr, Collections.reverseOrder());
        } else if (dist == Distribution.NEARLY_SORTED) {
            java.util.Arrays.sort(arr);
            int swaps = Math.max(1, (int) (n * 0.05));
            for (int i = 0; i < swaps; i++) {
                int i1 = rng.nextInt(n);
                int i2 = rng.nextInt(n);
                T tmp = arr[i1];
                arr[i1] = arr[i2];
                arr[i2] = tmp;
            }
        }
        // RANDOM is already shuffled
    }

    private static Comparable[] copyArray(Comparable[] source) {
        Comparable[] copy = new Comparable[source.length];
        System.arraycopy(source, 0, copy, 0, source.length);
        return copy;
    }

    @SuppressWarnings("unchecked")
    private static boolean isSorted(Comparable[] arr) {
        for (int i = 0; i < arr.length - 1; i++) {
            if (arr[i].compareTo(arr[i + 1]) > 0) return false;
        }
        return true;
    }
}
