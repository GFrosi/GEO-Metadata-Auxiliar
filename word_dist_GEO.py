import editdistance
import sys
import pandas as pd
from pprint import pprint
from tqdm import tqdm



def csv_open(csv_file):

    '''receives a csv file and returns a df'''

    df = pd.read_csv(csv_file)

    return df

def get_GSE_info(df):

    '''receives a df and returns a list of unique GSEs (series)'''

    GSE_list = list(set(df['GSE'].tolist()))

    return GSE_list


def create_list_dfs(df, GSE_list):

    '''receives a df and a list of GSEs and returns a list of dfs'''

    list_dfs = []
    for gse in GSE_list:

        sub_df = df[df['GSE'].str.contains(gse)]

        list_dfs.append(sub_df)

    return list_dfs


def list_input_IP(list_dfs):
    
    '''receives a list of df and returns two lists of lists of tuples containing the GSM and GSM title for each 
    input and IP samples per series (each sublist is related with a GSE)'''

    big_list_input = []
    big_list_IP = []

    for df in list_dfs:

        local_input = []
        local_IP = []
        
        for index, row in df.iterrows():

            try:

                if 'INPUT' in row['Target-GEO']: #so far Ok, but all 

                        # print(row['GSM'])

                    local_input.append((row['GSM'],row['GSM_title']))
            
                else:

                    local_IP.append((row['GSM'],row['GSM_title']))
        
            except:

                print("An exception occurred. Check the GSEs")

        big_list_input.append(local_input)
        big_list_IP.append(local_IP)

    return big_list_input, big_list_IP #list of list of tuples with GSM and GSM title
   

def create_big_data(big_list_IP):

    '''receives two lists of lists of tuples and returns a list of IPs per series'''

    big_data = []

    for ip in big_list_IP:

        data = []

        for gsm in ip: #tuples

            word_ip = gsm[1]

            data.append(word_ip)

        big_data.append(data)
        
    return big_data


def count_dist(big_list_input, big_data):

    dict_dist = {}

    # big_dist = []

    for input, ip in zip(big_list_input,big_data):

        # local_dist = []
        # print(input, ip)

        for inp in input:

            name_inp = inp[1]

            for record in ip:

                # print(ele)
                dist = editdistance.eval(record, name_inp)
                
                # local_dist.append((inp[0],record, dist))
                if record not in dict_dist.keys():
                    dict_dist[record] = [(inp[0], dist)]
                else:
                    tup = (inp[0], dist)
                    dict_dist[record].append(tup)

                # print(name_inp, inp[0],record, dist)
    return dict_dist


def sort_tuple(list_tup):
    
    '''Receives a list of tuples with Input and min value, and returns a list of corresponding
    input(s)'''

    min_list_gsm = []
    list_tup.sort(key = lambda x: x[1]) 

    min = list_tup[0][1]
    # print(min)
    for score in list_tup:
        if min == score[1]:
            min_list_gsm.append(score[0])

    # print(list_tup)
    return min_list_gsm
    

def filter_min(dict_dist):
    # pprint(dict_dist)

    '''receives a dict of distances (key: IP sample; value: list of tuples), and returns
    a filtered list of tuples with the corresponding inputs per IP samples'''

    filtered_list_of_tup = [] 

    for k,v in dict_dist.items():
        min_list_gsm = sort_tuple(v)

        min_list_gsm.append(k)
        
        # final_tup = (tup[0][0],k)
        filtered_list_of_tup.append(min_list_gsm)

    return filtered_list_of_tup


def create_col(df, filtered_list_of_tup):

    '''receives a df and a list of lists, and returns a list with corresponding 
    inputs per IP to be added into a new column'''

    list_final = ['NA'] *len(df)

    count = 0

    for index, row in tqdm(df.iterrows()):

        for ele in filtered_list_of_tup:

            if ele[-1] in row['GSM_title']:

                input = ','.join(ele[:-1])
                
                list_final[count] = input

                break

        count +=1
                
    return list_final


def add_col(df, list_final):

    df1 = df.copy()

    df1['Corresponding_Input'] = list_final

    return df1



def main():

    df = csv_open(sys.argv[1])
    path = sys.argv[2]

    # print(table)
    GSE_list = get_GSE_info(df)
    list_dfs = create_list_dfs(df, GSE_list)
    big_list_input, big_list_IP = list_input_IP(list_dfs)
    # print(big_list_input,big_list_IP)
    # sys.exit()
    big_data = create_big_data(big_list_IP)
    # print(big_data)
    # sys.exit()
    dict_dist = count_dist(big_list_input,big_data)
    filtered_list_of_tup = filter_min(dict_dist)
    list_final = create_col(df, filtered_list_of_tup)
    df_final = add_col(df, list_final)
    df_final.to_csv(path)


if __name__ == "__main__":

    main()