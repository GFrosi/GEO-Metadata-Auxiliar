from os import set_inheritable
import editdistance
import sys
import pandas as pd
from pprint import pprint
from tqdm import tqdm
from time import sleep



def csv_open(csv_file):
    '''receives a csv file 
    and returns a df'''

    df = pd.read_csv(csv_file)

    return df


def get_GSE_info(df):
    '''receives a df and 
    returns a list of unique 
    GSEs (series)'''

    GSE_list = list(dict.fromkeys(df['GSE'].tolist()))
    
    return GSE_list


def create_list_dfs(df, GSE_list):
    '''receives a df and a list of GSEs 
    and returns a list of dfs'''

    list_dfs = []

    for gse in GSE_list:
        sub_df = df[df['GSE'].str.match(gse)]
        list_dfs.append(sub_df)
     
    return list_dfs


def list_input_IP(list_dfs):
    '''receives a list of df and returns 
    two lists of lists of tuples containing 
    the GSM and GSM title for each input and IP 
    samples per series (each sublist is related 
    with a GSE)'''

    big_list_input = []
    big_list_IP = []

    for df in list_dfs:
        local_input = []
        local_IP = []
        
        for index, row in df.iterrows():
            try:
                if 'INPUT' in row['Target-GEO']: 
                    local_input.append((row['GSM'],row['GSM_title'],row['GSE']))
            
                else:
                    local_IP.append((row['GSM'],row['GSM_title'],row['GSE']))
        
            except:
                print("An exception occurred. Check the GSEs")

        big_list_input.append(local_input)
        big_list_IP.append(local_IP)

    return big_list_input, big_list_IP #list of list of tuples with GSM and GSM title
   

def checking_similarity_gse(big_list_input, big_list_IP):
    '''receives a list of list of tuples related to input 
    and IP samples. If the number of GSE does not match, 
    the code will break'''

    list_input_check = []
    list_ip_check = []

    #input
    for i in big_list_input:
        for ele in i:
            list_input_check.append(ele[-1])
    
        list_input_GSE = list(dict.fromkeys(list_input_check))
    
    #IP
    for i in big_list_IP:
        for ele in i:
            list_ip_check.append(ele[-1])
    
        list_ip_GSE = list(dict.fromkeys(list_ip_check))

    input = set(list_input_GSE)
    ip = set(list_ip_GSE)

    result_input_minus_ip = input - ip
    result_ip_minus_input = ip - input 

    if len(result_input_minus_ip) != 0 or len(result_ip_minus_input) != 0:
        list1 = list(result_input_minus_ip)
        list2 = list(result_ip_minus_input)

        print(f'GSE(s) specific(s) for Input samples:{result_input_minus_ip}')
        print()
        print('\n'.join(list1))
        print()
        print(f'GSE(s) specific(s) for IP samples:{result_ip_minus_input}')
        print()
        print('\n'.join(list2))
        print()
        print('You should remove those GSEs and re-run the script')

        sys.exit(1)

    else:
        print('Check completed, your INPUT table is correct!')


def create_big_data(big_list_IP):
    '''receives a lists of lists 
    of tuples and returns a list 
    of IPs per series'''

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
    
    for input, ip in zip(big_list_input,big_data):
        for inp in input:
            name_inp = inp[1]

            for record in ip:
                dist = editdistance.eval(record, name_inp)
                
                if record + '$' + inp[-1] not in dict_dist.keys():
                    dict_dist[record + '$' + inp[-1]] = [(inp[0], dist)]
                else:
                    tup = (inp[0], dist)
                    dict_dist[record + '$' + inp[-1]].append(tup)

    return dict_dist


def sort_tuple(list_tup):
    '''Receives a list of tuples 
    with Input and min value, and 
    returns a list of corresponding
    input(s)'''

    min_list_gsm = []
    list_tup.sort(key = lambda x: x[1]) 

    min = list_tup[0][1]

    for score in list_tup:
        if min == score[1]:
            min_list_gsm.append(score[0])

    return min_list_gsm
    

def filter_min(dict_dist):
    '''receives a dict of distances 
    (key: IP sample; value: list of tuples),
    and returns a filtered list of tuples with 
    the corresponding inputs per IP samples'''

    filtered_list_of_tup = [] 

    for k,v in dict_dist.items():
        min_list_gsm = sort_tuple(v)
        new_k = k.split('$')[0]

        min_list_gsm.append(new_k)

        filtered_list_of_tup.append(min_list_gsm)

    return filtered_list_of_tup


def create_col(df, filtered_list_of_tup):
    '''receives a df and a list of lists, 
    and returns a list with corresponding 
    inputs per IP to be added into a new column'''

    list_final = ['NA'] *len(df)
    count = 0

    for index, row in tqdm(df.iterrows()):
        for ele in filtered_list_of_tup:
            if ele[-1] == row['GSM_title']:
                input = ','.join(ele[:-1])
                list_final[count] = input
                
                break

        count +=1

    return list_final


def add_count_corres_input(list_final):
    '''Receives a list of corresponding 
    inputs per sample and return a list of 
    counts per sample'''

    list_count = []

    for ele in list_final:

        if ele == 'NA':
            result = 0
            list_count.append(result)
        
        else:
            count = ele.split(',')
            result = len(count)
            list_count.append(result)

    return list_count


def add_col(df, list_final, list_count):
    '''receives a df and a list and return 
    a df with a new column'''

    df1 = df.copy()

    df1['Corresponding_Input'] = list_final
    df1['Corresponding_Input_Count'] = list_count

    return df1


def main():

    df = csv_open(sys.argv[1])
    path = sys.argv[2]
    GSE_list = get_GSE_info(df)
    list_dfs = create_list_dfs(df, GSE_list)
    big_list_input, big_list_IP = list_input_IP(list_dfs)
    checking_similarity_gse(big_list_input,big_list_IP)
    big_data = create_big_data(big_list_IP)
    dict_dist = count_dist(big_list_input,big_data)
    filtered_list_of_tup = filter_min(dict_dist)
    list_final = create_col(df, filtered_list_of_tup)
    list_count = add_count_corres_input(list_final)
    df_final = add_col(df, list_final, list_count)
    df_final.to_csv(path)


if __name__ == "__main__":

    main()