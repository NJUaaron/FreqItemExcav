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


class treeNode:
    def __init__(self, name, count, parent):
        self.name = name        #item
        self.count = count      #计数
        self.nodeLink = None    #节点链的下一位置
        self.parent = parent
        self.children = {}

    def add_count(self, count):
        self.count += count


def insert_tree(trans, T, headerTable, count):
    p = trans[0]        #第一个元素
    P = trans[1::]      #剩余元素列表
    if p in T.children:
        #第一个元素已在T的子女中
        T.children[p].add_count(count)
    else:
        #创建一个新节点
        T.children[p] = treeNode(p, count, T)
        #将新节点添加到项头表的节点链尾部
        if headerTable[p][1] == None:
            headerTable[p][1] = T.children[p]
        else:
            ptr = headerTable[p][1]
            while ptr.nodeLink != None:
                ptr = ptr.nodeLink
            ptr.nodeLink = T.children[p]
    #递归
    if len(P) > 0:
        insert_tree(P, T.children[p], headerTable, count)


def createFPtree(data_set, min_sup):
    #项头表
    headerTable = {}
    for trans in data_set:
        for item in trans:
            if item in headerTable:
                headerTable[item] += 1
            else:
                headerTable[item] = 1
    for k in list(headerTable.keys()):
        if headerTable[k] < min_sup:
            del(headerTable[k])     # 删除不满足最小支持度的项
    if len(headerTable) == 0:
        return None, None
    for i in headerTable:
        headerTable[i] = [headerTable[i], None] #项ID:[支持度计数, 节点链]

    #FPtree
    FPtree = treeNode('null', 1, None)
    for trans in data_set:
        orderd_trans = trans.copy()
        #删去不频繁的项
        for i in range(len(orderd_trans) - 1, -1, -1):
            if orderd_trans[i] not in headerTable:
                del orderd_trans[i]
        # 根据全局频数从大到小对单样本降序排序
        orderd_trans.sort(key=lambda p: headerTable[p][0], reverse=True)
        #插入FPtree中
        if len(orderd_trans) > 0:
            insert_tree(orderd_trans, FPtree, headerTable, 1)

    return FPtree, headerTable


def createCondFPtree(condPats, min_sup):
    #项头表
    headerTable = {}
    for pat in condPats:
        for item in pat:
            if item in headerTable:
                headerTable[item] += condPats[pat]
            else:
                headerTable[item] = condPats[pat]
    for k in list(headerTable.keys()):
        if headerTable[k] < min_sup:
            del(headerTable[k])     # 删除不满足最小支持度的项
    if len(headerTable) == 0:
        return None, None
    for i in headerTable:
        headerTable[i] = [headerTable[i], None]     #项ID:[支持度计数, 节点链]

    #FPtree
    FPtree = treeNode('null', 1, None)
    for pat in condPats:
        orderd_trans = list(pat)
        #删去不频繁的项
        for i in range(len(orderd_trans) - 1, -1, -1):
            if orderd_trans[i] not in headerTable:
                del orderd_trans[i]
        # 根据全局频数从大到小对单样本降序排序
        orderd_trans.sort(key=lambda p: headerTable[p][0], reverse=True)
        #插入FPtree中
        if len(orderd_trans) > 0:
            insert_tree(orderd_trans, FPtree, headerTable, condPats[pat])

    return FPtree, headerTable


def findCondPatternBase(pat, headerTable):
    node = headerTable[pat][1]
    condPats = {}
    while node != None:
        prefix = []
        ptr = node
        while ptr.parent != None:
            prefix.append(ptr.name)
            ptr = ptr.parent
        if len(prefix) > 1:
            condPats[tuple(prefix[1:])] = node.count
        node = node.nodeLink
    return condPats


def FP_growth(FPtree, pre, headerTable, L, min_sup):
    for pat in headerTable:
        newPat = [pat] + pre
        L[tuple(newPat)] = headerTable[pat][0]
        condPats = findCondPatternBase(pat, headerTable)
        newFP, newHT = createCondFPtree(condPats, min_sup)

        if newFP != None:
            FP_growth(newFP, newPat, newHT, L, min_sup)


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
    min_conf = 0.3      #最小置信度

    ################读入数据################
    data_set = load_data_set2()

    ##############生成频繁项集##############
    time_start = time.time()
    L = {}
    FPtree, headerTable = createFPtree(data_set, min_sup)
    if FPtree != None:
        FP_growth(FPtree, [], headerTable, L, min_sup)

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
