# Komplexity

A tool that estimates sequence complexing by counting distinct k-mers in sliding windows

## Installation

```
pip install git+git@github.com:zyndagj/komplexity.git
```

## Usage

```
usage: komplexity [-h] -F FASTA [-O BEDG] [-k INT] [-w INT] [-s INT] [-P INT]

A tool that estimates sequence complexing by counting distinct k-mers in
sliding windows

optional arguments:
  -h, --help  show this help message and exit
  -F FASTA    Input genome
  -O BEDG     Output file (Default: stdout)
  -k INT      k-mer size (Default: 21)
  -w INT      Window size (Default: 10000)
  -s INT      Step (slide) size (Default: 1000)
  -P INT      Number of cores to use (Default: 8)
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
