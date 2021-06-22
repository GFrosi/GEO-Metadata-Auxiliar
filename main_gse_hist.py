import pandas as pd 
import numpy as np 
import sys


def create_dict(df):

    '''This function receives a df generated from a csv file. It will return a dict with the GSE as keys
    and a list of histones (k4me3, k4me1, k27me3, k27ac, k9me3, k36me3 and input) as values'''


    dict_gse_hist = {}
    for i, row in df.iterrows():
    
        if row['GSE'] not in dict_gse_hist.keys():
            dict_gse_hist[row['GSE']] = list([row['Target-GEO']])
    
        else:
            dict_gse_hist[row['GSE']].append(row['Target-GEO'])

    return dict_gse_hist


def set_values(dict_gse_hist):

    '''This function receives a dictionary (GSE as keys and list of histones as values)
    It will return a dict where the list of set of histones.'''

    new_dict = {}

    for k,v in dict_gse_hist.items():
        # print('GSE:',k,'histone:',v)

        new_dict[k] = list(set(v))

    return(new_dict)


def create_len_hist(df, new_dict):

    '''This function receives a dataframe and a dictionary (GSE as keys and a list of set of histones as values.
    It will return a list with the len values (how many histones a GSE has).'''

    list_len = []

    for i, row in df.iterrows():

        if row['GSE'] in new_dict.keys():

            list_len.append(len(new_dict[row['GSE']]))
        
        else:
            print(row['GSE'], 'not exist')

            sys.exit(1)

    return list_len


def create_col(df, list_len):

    '''This function receives a df and a list. It will return a df with a new column'''

    df1 = df.copy()

    df1['N_Histone_Class'] = list_len

    return df1



def main():

    df = pd.read_csv(sys.argv[1]) #path to the dataframe

    dict_gse_hist = create_dict(df)

    new_dict = set_values(dict_gse_hist)
    
    list_new_col = create_len_hist(df, new_dict)

    final_df = create_col(df, list_new_col)

    final_df.to_csv(sys.argv[2], index=False) #path to the output file with a new column



if __name__ == "__main__":

    main()

