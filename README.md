# GEO-Metadata-Auxiliary

## Scripts to create new columns (histones count and corresponding inputs per IP samples) using the GEO-METADATA dataframe.

# Requirements

```python >= 3.7 and create a env with requirements.txt```

### main_gse_hist.py

1. This script receives a dataframe with at least the 'GSE' and 'Target-GEO' columns as the first argument, and a path to the output file as the second argument. It will returns the dataframe including a new column 'N_Histone_Class',
including the input samples as a class.

- To tun this script:
```python main_gse_hist.py <dataframe.csv> <path_to_output_file>```

### word_dist_GEO.py

2. This scripts receives a dataframe with at least the 'GSE', 'GSM_title' and 'Target-GEO' as the first argument and a path to the output file as the second argument. It will returns a dataframe with a new column 'Corresponding_input', with the correspondent input samples (GSM(s)) for each IP sample for each series (GSE). The script imports the editdistance library, which uses the Levenshtein distance to calculate the difference between strings. 

- To run this script:
```python word_dist_GEO.py <dataframe.csv> <path_to_output_file>```

You can run both scripts using the 'test_GSEs.csv' file

