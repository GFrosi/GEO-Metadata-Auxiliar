import pandas as pd
import sys
import argparse


def filter_input_h3k(df):
    '''Receives a df. Returns
    a df with GSEs which contains 
    input and histones (H3k) samples'''

    df_gse_input = df[df['Target-GEO'].str.contains('input|mock', case=False)].reset_index()
    list_gse_input = df_gse_input['GSE'].tolist()
    df_H3K = df[df['Target-GEO'].str.contains('H3K', case=False)].reset_index()
    list_gse_h3k = df_H3K['GSE'].tolist()
    inters_gse_input_h3k = list(set(list_gse_h3k).intersection(set(list_gse_input)))
    df_filter_GSE_input_H3k = df[df['GSE'].isin(inters_gse_input_h3k)]
    df_gse_filtered = df_filter_GSE_input_H3k[df_filter_GSE_input_H3k['Target-GEO'].str.contains('H3K|input', case=False)]
    
    return df_gse_filtered
    

def get_hist_interest(df_gse_filtered):
    '''Receives a df with inputs and histones (H3k
    and returns a df with histones of interest (6 class)'''

    df_gse_histones_interest = df_gse_filtered[df_gse_filtered['Target-GEO'].str.contains('H3K4me3|H3k4me1|H3k27me3|H3k27ac|H3k9me3|H3k36me3|input', case=False)]

    return df_gse_histones_interest


def create_dict(df_gse_histones_interest):
    '''This function receives a df generated 
    from a csv file. It will return a dict with 
    the GSE as keys and a list of histones 
    (k4me3, k4me1, k27me3, k27ac, k9me3, k36me3 
    and input) as values'''

    dict_gse_hist = {}

    for i, row in df_gse_histones_interest.iterrows():
        if row['GSE'] not in dict_gse_hist.keys():
            dict_gse_hist[row['GSE']] = list([row['Target-GEO']])
    
        else:
            dict_gse_hist[row['GSE']].append(row['Target-GEO'])

    return dict_gse_hist


def set_values(df_gse_histones_interest):
    '''This function receives a dataframe 
    It will return a dict where the list of set 
    of histones.'''

    dict_gse_hist = create_dict(df_gse_histones_interest)

    new_dict = {}

    for k,v in dict_gse_hist.items():
        new_dict[k] = list(set(v))

    return(new_dict)


def create_len_hist(df_gse_histones_interest, new_dict):
    '''This function receives a dataframe and a dictionary 
    (GSE as keys and a list of set of histones as values.
    It will return a list with the len values (how many histones 
    a GSE has).'''

    list_len = []

    for i, row in df_gse_histones_interest.iterrows():
        if row['GSE'] in new_dict.keys():
            list_len.append(len(new_dict[row['GSE']]))
        
        else:
            print(row['GSE'], 'not exist')
            sys.exit(1)

    return list_len


def create_col(df_gse_histones_interest, new_dict):
    '''This function receives a df and a list. It will 
    return a df with a new column'''

    list_len = create_len_hist(df_gse_histones_interest, new_dict)
    df1 = df_gse_histones_interest.copy()
    df1['N_Histone_Class'] = list_len

    return df1


def main():

    df_geo = pd.read_csv(args.df, keep_default_na=False) #df with ngs and chip atlas 
    df_gses_filtered = filter_input_h3k(df_geo)
    df_gses_filtered.to_csv(args.path, index=False)
    df_gse_histones_interest = get_hist_interest(df_gses_filtered)
    new_dict = set_values(df_gse_histones_interest)
    df_hist_nb_class = create_col(df_gse_histones_interest, new_dict)
    df_hist_nb_class.to_csv(args.PATH, index=False) 


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = 'A tool to manipulate the GEO metadata table and return a dataframe of Histone of interest (H3k input and the 6 major histones)'
    )
    
    parser.add_argument('-d', '--df', action='store',
                        help='The absolut path to the GEO metadata dataframe',
                        )

    parser.add_argument('-p', '--path', action='store',
                        help='The absolut path to save the dataframe containing the H3k and input samples',
                        )
    
    parser.add_argument('-P', '--PATH', action='store',
                        help='The absolut path to save the dataframe containing the the number of histone class column',
                        )

    args = parser.parse_args()

    
    main()
