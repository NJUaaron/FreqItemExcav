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



def find_frequent_1_items(data_set, min_sup):
    L1 = {}     #频繁1-项集（字典）
    for itemset in data_set:
        for item in itemset:
            if (item,) in L1:          #项已在字典中
                L1[(item,)] += 1     #字典的key是tuple类型，才能散列（list不行）
            else:
                L1[(item,)] = 1

    #去掉计数小于最小支持度的项
    for key in list(L1.keys()):     #必须将L1.keys()转换成list，否则会报错
        if L1[key] < min_sup:
            del L1[key]

    return L1


def has_infrequent_subset(c, L_km1):
    for i in range(len(c)):
        s = c.copy()
        del s[i]        #s是c的一个k-1子集
        if tuple(s) not in L_km1:
            return True
    return False


def aproiri_gen(L_km1, k):     #从频繁(k-1)-项集构造候选候选k-项集
    C_k = []
    for itemset1 in L_km1:
        for itemset2 in L_km1:
            concate = True
            for i in range(k - 2):
                if itemset1[i] != itemset2[i]:
                    concate = False
                    break
            if itemset1[k - 2] >= itemset2[k - 2]:
                concate = False
            if concate:     #可以连接itemset1和itemset2
                c = list(itemset1)
                c.append(itemset2[k - 2])
                if not has_infrequent_subset(c, L_km1):
                    C_k.append(c)
    return C_k


def pruning(C_k, data_set, min_sup):       #从Ck到Lk，删除不频繁的候选
    count = [0 for x in range(len(C_k))]
    for t in data_set:
        for i in range(len(C_k)):
            label = True
            for item in C_k[i]:
                if item not in t:
                    label = False
                    break
            if label:
                count[i] += 1

    #将C_k中计数不小于最小支持度的项加入L_k中
    L_k = {}
    for i in range(len(count)):
        if count[i] >= min_sup:
            L_k[tuple(C_k[i])] = count[i]
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
    min_sup = 20      #最小支持度
    min_conf = 0      #最小置信度

    ################读入数据################
    data_set = load_data_set2()

    ##############生成频繁项集##############
    time_start = time.time()
    L = find_frequent_1_items(data_set, min_sup)    #所有的频繁项集
    L_km1 = L           #L_k-1 上一轮产生的频繁项集

    #print("L1: ")
    #print(L)

    k = 2   #k-项集
    while len(L_km1) != 0:
        C_k = aproiri_gen(L_km1, k)     #生成Ck
        L_k = pruning(C_k, data_set, min_sup)    #生成Lk
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



