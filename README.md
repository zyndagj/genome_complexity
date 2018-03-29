# Komplexity

A tool that estimates sequence complexing by counting distinct k-mers in sliding windows

## Installation

```
pip install git+https://github.com/zyndagj/komplexity.git
```

## Usage

```
usage: komplexity [-h] -F FASTA [-O BEDG] [-k INT] [-w INT] [-s INT] [-P INT]
                   [-A STR] [-M STR] [-N]

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
  -M STR      Report unique, duplicate, and max kmers (Default: unique)
  -N          Allow N's in k-mers
```

### Reporting

**Unique** - Reports the number of distinct k-mers in a window

```
unique({AA, AA, AA, AC}) = 2
```

**Duplicate** - Reports the number of k-mers seen at least twice

```
duplicate({AA, AA, AA, AC}) = 1
```

**Max** - Reports the highest k-mer frequency

```
max({AA, AA, AA, AC}) = 3
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

### Example Results

When run on the TAIR10 reference using 29 base k-mers and 10 kilobase windows that slide 1 kilobase each step using:

```
komplexity -F TAIR10_Chr.all.fasta -k 29 -w 10000 -s 1000 -M max -O TAIR10_k29_w10000_s1000_max_noN.bedgraph
komplexity -F TAIR10_Chr.all.fasta -k 29 -w 10000 -s 1000 -M unique -O TAIR10_k29_w10000_s1000_unique_noN.bedgraph
komplexity -F TAIR10_Chr.all.fasta -k 29 -w 10000 -s 1000 -M duplicate -O TAIR10_k29_w10000_s1000_duplicate_noN.bedgraph
```

Komplexity produces 3 three tracks in bedgraph format. These tracks can be viewed directly in a genome browser like IGV.

The first image below is centered around the centromere of *A. thaliana* Chromosome 3.

![tair10_centromere](https://user-images.githubusercontent.com/6790115/38102090-d7e55510-3347-11e8-90cf-946e7f06ca80.png)

The unique track dips around repetitive and regions containing N bases since those k-mers are not reported. You can also see that both the duplicate and max tracks spike around those regions, demonstrating the not only are there fewer distinct k-mers, but they are also getting repeated in the sequence window. Lastly, you'll see that there are a few spikes in the max track that do not correspond to major changes in either the duplicate or unique tracks.

![tair10_arm](https://user-images.githubusercontent.com/6790115/38102322-7f1289fc-3348-11e8-8a13-d3413ba6c3f8.png)

Looking at a region on the arm of *A. thaliana* Chromosome 3, you'll see a large spike in the duplicate track that corresponds to the only obvious dip in the unique track. You'll also see smaller spikes in duplicate that align to spikes in max and transposable elements from the [Araport11](https://www.araport.org/) annotation.
