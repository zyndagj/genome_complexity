# Komplexity

A tool that estimates sequence complexing by counting distinct k-mers in sliding windows

## Installation

```
pip install git+https://github.com/zyndagj/komplexity.git
```

## Usage

```
usage: komplexity [-h] -F FASTA [-O BEDG] [-k INT] [-w INT] [-s INT] [-P INT]
                   [-A STR] [-N]

A tool that estimates sequence complexing by counting distinct k-mers in
sliding windows

optional arguments:
  -h, --help  show this help message and exit
  -F FASTA    Input genome
  -O BEDG     Output file (Default: stdout)
  -k INT      k-mer size (Default: 21)
  -w INT      Window size (Default: 10000)
  -s INT      Step (slide) size (Default: 1000)
  -P INT      Number of cores to use (Default: 28)
  -A STR      Aggregation method ([mean], median, sum, min, max)
  -N          Allow N's in k-mers
```

## Testing

```
python setup.py test
```

## Output

By default bedgraph formatted output is sent to STDOUT, but it can be sent to a specific file with the `-O` argument. The output has four columns as follows:

- Chromosome
- Start position (0-based)
- End position (exclusive)
- Number of distinct k-mers

A line will be outupt for every sliding step, and overlapping windows will be aggregated using the (`-A`) method. For example, if we used 4 base windows, 2 base steps, and counted 2-mers, we would have the following results

```
Sequence AGAGCCTT
Window 1 ||||      2 2-mers (AG,GA)
Window 2   ||||    3 2-mers (AG,GC,CT)
Window 3     ||||  3 2-mers (CC,CT,TT)

Output Bedgraph with sum aggregation

Sequence  0 2 2
Sequence  2 4 5
Sequence  4 6 6
Sequence  6 8 3
```

Notice that there was an output entry for step, instead of aligning to windows. This is because the bedgraph format does not allow for overlapping results.
