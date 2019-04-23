import pandas as pd
import time

def load_data_set1():
    #数据所在路径
    filepath = r'G:\学习\大三下\数据挖掘\Assignment2\dataset\GroceryStore\Groceries.csv'
    df = pd.read_csv(filepath)
    Items = df['items']     #items列数据
    data_set = []
    for item in Items:
        b = 1
        data = []
        for i in range(1, len(item)):   #遍历一个记录(record)中的每一个字符
            if item[i] == ',' or item[i] == '}':
                data.append(item[b: i])
                b = i + 1
        data_set.append(data)
    return data_set


def load_data_set2():
    #数据所在路径
    filepath = r'G:\学习\大三下\数据挖掘\Assignment2\dataset\UNIX_usage\USER0\sanitized_all.981115184025'
    data_set = []

    with open(filepath, 'r') as f:
        textlist = f.readlines()
    itemset = set()
    for i in range(1, len(textlist)):
        textlist[i] = textlist[i].strip('\n')
        if textlist[i] == "**SOF**":
            itemset = set()
        elif textlist[i] == "**EOF**":
            if len(itemset) > 0:
                data_set.append(list(itemset))
        else:
            itemset.add(textlist[i])

    return data_set


def FindkSubset(set, k):    #找到所有k长子集
    #generate all combination of N items(all 0 and all 1 is out)
    N = len(set)
    #enumerate the 2**N-1 possible combinations
    subsetList = []

    for i in range(2**N):
        subset = []

        #calculte 1's number in i
        count1 = 0
        for j in range(N):
            if(i >> j) % 2 == 1:
                count1 += 1
        if count1 != k:
            continue

        for j in range(N):
            #test jth bit of integer i
            if(i >> j) % 2 == 1:
                subset.append(set[j])

        subsetList.append(subset)
    return subsetList


def exhau_gen(data_set, k, min_sup):
    C_k = {}
    L_k = {}

    for itemset in data_set:
        sList = FindkSubset(itemset, k)
        for set in sList:
            set.sort()
            if tuple(set) in C_k:
                C_k[tuple(set)] += 1
            else:
                C_k[tuple(set)] = 1

    for key in C_k:
        if C_k[key] >= min_sup:
            L_k[key] = C_k[key]
    return L_k


def FindAllSubset(set):
    #generate all combination of N items(all 0 and all 1 is out)
    N = len(set)
    #enumerate the 2**N-2 possible combinations
    subsetList = []
    anti_subsetList = []
    for i in range(1, 2**N-1):
        subset = []         #非空子集
        anti_subset = []    #非空子集的补集
        for j in range(N):
            #test jth bit of integer i
            if(i >> j) % 2 == 1:
                subset.append(set[j])
            else:
                anti_subset.append(set[j])
        subsetList.append(subset)
        anti_subsetList.append(anti_subset)
    return subsetList, anti_subsetList



if __name__ == "__main__":
    min_sup = 80       #最小支持度
    min_conf = 0.3      #最小置信度

    ################读入数据################
    data_set = load_data_set2()

    ##############生成频繁项集##############
    time_start = time.time()
    L = exhau_gen(data_set, 1, min_sup)
    L_km1 = L

    #print("L1: ")
    #print(L)

    k = 2   #k-项集
    while len(L_km1) != 0:
        L_k = exhau_gen(data_set, k, min_sup)       #生成Lk
        L_km1 = L_k

        #print("L" + str(k) +":")
        #print(L_k)

        L.update(L_k)   #L_k并入L中
        k += 1

    time_end = time.time()
    print('Total cost', time_end - time_start)
    print(L)

    ##############产生关联规则##############
    for freqitem in L:
        sup_l = L[freqitem]
        subsetList, anti_subsetList = FindAllSubset(list(freqitem))
        for i in range(len(subsetList)):
            s = tuple(subsetList[i])
            anti_s = tuple(anti_subsetList[i])
            sup_s = L[s]
            if sup_l/sup_s >= min_conf:
                #输出关联规则
                print(s, end='')
                print(" => ", end='')
                print(anti_s, end='')
                print("   sup: " + str(sup_l) + " conf: " + str(round(sup_l/sup_s, 3)))



