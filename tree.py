# coding=utf-8
import xlrd
import xlwt
import math
import operator
from sklearn import datasets

from app.db import query


##计算给定数据集的信息熵
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():  # 为所有可能分类创建字典
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key]) / numEntries
        shannonEnt -= prob * math.log(prob, 2)  # 以2为底数求对数
    return shannonEnt


'''
#创建数据
def createDataSet():
    dataSet = [[1,1,'yes'],
               [1,1,'yes'],
               [1,0,'no'],
               [0,1,'no'],
               [0,1,'no']]
    labels = ['no surfacing', 'flippers']
    return dataSet, labels
'''
def createDateSet():
    datas = query('stock_compare000033',
                  'date, high, close, low, volume, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover, p_change')
    dataSet = []
    for data in datas:
        curr = [
            data[1], data[2], data[3], data[4],
            data[5], data[6], data[7], data[8],
            data[9], data[10], data[11], data[12]
        ]
        dataSet.append(curr)
    labels = [
        'high', 'close', 'low', 'volume',
        'ma5', 'ma10', 'ma20', 'v_ma5',
        'v_ma5', 'v_ma10', 'v_ma20', 'p_change']
    return dataSet, labels


# 依据特征划分数据集  axis代表第几个特征  value代表该特征所对应的值  返回的是划分后的数据集
def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis + 1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet


'''
#ID3中的做法
#选择最好的数据集(特征)划分方式  返回最佳特征下标
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1   #特征个数
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):   #遍历特征 第i个
        featureSet = set([example[i] for example in dataSet])   #第i个特征取值集合
        newEntropy= 0.0
        for value in featureSet:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)   #该特征划分所对应的entropy
        infoGain = baseEntropy - newEntropy

        if infoGain > bestInfoGain:
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature
'''


# 选择最好的数据集(特征)划分方式  返回最佳特征下标
def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1  # 特征个数
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGainrate = 0.0;
    bestFeature = -1
    for i in range(numFeatures):  # 遍历特征 第i个
        featureSet = set([example[i] for example in dataSet])  # 第i个特征取值集合
        newEntropy = 0.0
        splitinfo = 0.0
        for value in featureSet:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)  # 该特征划分所对应的entropy
            splitinfo -= prob * math.log(prob, 2)
        if not splitinfo:
            splitinfo = -0.99 * math.log(0.99, 2) - 0.01 * math.log(0.01, 2)
        infoGain = baseEntropy - newEntropy
        infoGainrate = float(infoGain) / float(splitinfo)
        if infoGainrate > bestInfoGainrate:
            bestInfoGainrate = infoGainrate
            bestFeature = i
    return bestFeature


# 创建树的函数代码   python中用字典类型来存储树的结构 返回的结果是myTree-字典
def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):  # 类别完全相同则停止继续划分  返回类标签-叶子节点
        return classList[0]
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)  # 遍历完所有的特征时返回出现次数最多的
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel: {}}
    del (labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]  # 得到的列表包含所有的属性值
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value), subLabels)
    return myTree


# 多数表决的方法决定叶子节点的分类 ----  当所有的特征全部用完时仍属于多类
def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0;
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)  # 排序函数 operator中的
    return sortedClassCount[0][0]


# 使用决策树执行分类
def classify(inputTree, featLabels, testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)  # index方法查找当前列表中第一个匹配firstStr变量的元素的索引
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else:
                classLabel = secondDict[key]
    return classLabel


# 决策树的存储
def storeTree(inputTree, filename):  # pickle序列化对象，可以在磁盘上保存对象
    import pickle
    fw = open(filename, 'w')
    pickle.dump(inputTree, fw)
    fw.close()


def grabTree(filename):  # 并在需要的时候将其读取出来
    import pickle
    fr = open(filename)
    return pickle.load(fr)


# -*- coding: cp936 -*-
import matplotlib.pyplot as plt

decisionNode = dict(boxstyle='sawtooth', fc='0.8')
leafNode = dict(boxstyle='round4', fc='0.8')
arrow_args = dict(arrowstyle='<-')


def plotNode(nodeTxt, centerPt, parentPt, nodeType):
    createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction', \
                            xytext=centerPt, textcoords='axes fraction', \
                            va='center', ha='center', bbox=nodeType, \
                            arrowprops=arrow_args)


# 使用文本注解绘制树节点
def createPlot():
    fig = plt.figure(1, facecolor='white')
    fig.clf()
    createPlot.ax1 = plt.subplot(111, frameon=False)
    plotNode('a decision node', (0.5, 0.1), (0.1, 0.5), decisionNode)
    plotNode('a leaf node', (0.8, 0.1), (0.3, 0.8), leafNode)
    plt.show()


# 获取叶子节点数目和树的层数
def getNumLeafs(myTree):
    numLeafs = 0
    firstStr = myTree.keys()[0]
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if (type(secondDict[key]).__name__ == 'dict'):
            numLeafs += getNumLeafs(secondDict[key])
        else:
            numLeafs += 1
    return numLeafs


def getTreeDepth(myTree):
    maxDepth = 0
    firstStr = myTree.keys()[0]
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if (type(secondDict[key]).__name__ == 'dict'):
            thisDepth = 1 + getTreeDepth(secondDict[key])
        else:
            thisDepth = 1
        if thisDepth > maxDepth: maxDepth = thisDepth
    return maxDepth


# 更新createPlot代码以得到整棵树
def plotMidText(cntrPt, parentPt, txtString):
    xMid = (parentPt[0] - cntrPt[0]) / 2.0 + cntrPt[0]
    yMid = (parentPt[1] - cntrPt[1]) / 2.0 + cntrPt[1]
    createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)


def plotTree(myTree, parentPt, nodeTxt):  # if the first key tells you what feat was split on
    numLeafs = getNumLeafs(myTree)  # this determines the x width of this tree
    depth = getTreeDepth(myTree)
    firstStr = myTree.keys()[0]  # the text label for this node should be this
    cntrPt = (plotTree.xOff + (1.0 + float(numLeafs)) / 2.0 / plotTree.totalW, plotTree.yOff)
    plotMidText(cntrPt, parentPt, nodeTxt)
    plotNode(firstStr, cntrPt, parentPt, decisionNode)
    secondDict = myTree[firstStr]
    plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD
    for key in secondDict.keys():
        if type(secondDict[
                    key]).__name__ == 'dict':  # test to see if the nodes are dictonaires, if not they are leaf nodes
            plotTree(secondDict[key], cntrPt, str(key))  # recursion
        else:  # it's a leaf node print the leaf node
            plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
            plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
            plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
    plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD


# if you do get a dictonary you know it's a tree, and the first element will be another dict

def createPlot(inTree):
    fig = plt.figure(1, facecolor='white')
    # fig.title("c4.5",size=14)
    fig.clf()
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)  # no ticks
    createPlot.ax1.set_title("c4.5\n", size=24)
    # createPlot.ax1 = plt.subplot(111, frameon=False) #ticks for demo puropses
    plotTree.totalW = float(getNumLeafs(inTree))
    plotTree.totalD = float(getTreeDepth(inTree))
    plotTree.xOff = -0.5 / plotTree.totalW;
    plotTree.yOff = 1.0;
    plotTree(inTree, (0.5, 1.0), '')
    plt.show()


def getCount(inputTree, dataSet, featLabels, count):
    # global num
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    # count=[]
    for key in secondDict.keys():
        rightcount = 0
        wrongcount = 0
        tempfeatLabels = featLabels[:]
        subDataSet = splitDataSet(dataSet, featIndex, key)
        tempfeatLabels.remove(firstStr)
        if type(secondDict[key]).__name__ == 'dict':
            getCount(secondDict[key], subDataSet, tempfeatLabels, count)
            # 在这里加上剪枝的代码，可以实现自底向上的悲观剪枝
        else:
            for eachdata in subDataSet:
                if str(eachdata[-1]) == str(secondDict[key]):
                    rightcount += 1
                else:
                    wrongcount += 1
            count.append([rightcount, wrongcount, secondDict[key]])
            # num+=rightcount+wrongcount


def cutBranch_downtoup(inputTree, dataSet, featLabels, count):  # 自底向上剪枝
    # global num
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():  # 走到最深的非叶子结点
        if type(secondDict[key]).__name__ == 'dict':
            tempcount = []  # 本将的记录
            rightcount = 0
            wrongcount = 0
            tempfeatLabels = featLabels[:]
            subDataSet = splitDataSet(dataSet, featIndex, key)
            tempfeatLabels.remove(firstStr)
            getCount(secondDict[key], subDataSet, tempfeatLabels, tempcount)
            # 在这里加上剪枝的代码，可以实现自底向上的悲观剪枝
            # 计算，并判断是否可以剪枝
            # 原误差率，显著因子取0.5
            tempnum = 0.0
            wrongnum = 0.0
            old = 0.0
            # 标准误差
            standwrong = 0.0
            for var in tempcount:
                tempnum += var[0] + var[1]
                wrongnum += var[1]
            old = float(wrongnum + 0.5 * len(tempcount)) / float(tempnum)
            standwrong = math.sqrt(tempnum * old * (1 - old))
            # 假如剪枝
            new = float(wrongnum + 0.5) / float(tempnum)
            if new <= old + standwrong and new >= old - standwrong:  # 要确定新叶子结点的类别
                '''
	        #计算当前各个类别的数量多少，然后，多数类为新叶子结点的类别
		tempcount1=0
		tempcount2=0
		for var in subDataSet:
		    if var[-1]=='0':
			tempcount1+=1
		    else:
			tempcount2+=1
		if tempcount1>tempcount2:
		    secondDict[key]='0'
		else:
		    secondDict[key]='1'
                '''
                # 误判率最低的叶子节点的类为新叶子结点的类
                # 在count的每一个列表类型的元素里再加一个标记类别的元素。
                wrongtemp = 1.0
                newtype = -1
                for var in tempcount:
                    if float(var[1] + 0.5) / float(var[0] + var[1]) < wrongtemp:
                        wrongtemp = float(var[1] + 0.5) / float(var[0] + var[1])
                        newtype = var[-1]
                secondDict[key] = str(newtype)
                tempcount = []  # 这个相当复杂，因为如果发生剪枝，才会将它置空，如果不发生剪枝，那么应该保持原来的叶子结点的结构
            for var in tempcount:
                count.append(var)
    for key in secondDict.keys():
        if type(secondDict[key]).__name__ == 'dict':
            continue
        rightcount = 0
        wrongcount = 0
        subDataSet = splitDataSet(dataSet, featIndex, key)
        for eachdata in subDataSet:
            if str(eachdata[-1]) == str(secondDict[key]):
                rightcount += 1
            else:
                wrongcount += 1
        count.append([rightcount, wrongcount, secondDict[key]])  # 最后一个为该叶子结点的类别


def cutBranch_uptodown(inputTree, dataSet, featLabels):  # 自顶向下剪枝
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():
        if type(secondDict[key]).__name__ == 'dict':
            tempfeatLabels = featLabels[:]
            subDataSet = splitDataSet(dataSet, featIndex, key)
            tempfeatLabels.remove(firstStr)
            tempcount = []
            getCount(secondDict[key], subDataSet, tempfeatLabels, tempcount)
            print tempcount
            # 计算，并判断是否可以剪枝
            # 原误差率，显著因子取0.5
            tempnum = 0.0
            wrongnum = 0.0
            old = 0.0
            # 标准误差
            standwrong = 0.0
            for var in tempcount:
                tempnum += var[0] + var[1]
                wrongnum += var[1]
            old = float(wrongnum + 0.5 * len(tempcount)) / float(tempnum)
            standwrong = math.sqrt(tempnum * old * (1 - old))
            # 假如剪枝
            new = float(wrongnum + 0.5) / float(tempnum)
            if new <= old + standwrong and new >= old - standwrong:  # 要确定新叶子结点的类别
                '''
                #计算当前各个类别的数量多少，然后，多数类为新叶子结点的类别
            tempcount1=0
            tempcount2=0
            for var in subDataSet:
                if var[-1]=='0':
                tempcount1+=1
                else:
                tempcount2+=1
            if tempcount1>tempcount2:
                secondDict[key]='0'
            else:
                secondDict[key]='1'
                    '''
                # 误判率最低的叶子节点的类为新叶子结点的类
                # 在count的每一个列表类型的元素里再加一个标记类别的元素。
                wrongtemp = 1.0
                newtype = -1
                for var in tempcount:
                    if float(var[1] + 0.5) / float(var[0] + var[1]) < wrongtemp:
                        wrongtemp = float(var[1] + 0.5) / float(var[0] + var[1])
                        newtype = var[-1]
                secondDict[key] = str(newtype)


if __name__ == '__main__':
    global num
    num = 0
    dataset, labels = createDateSet()
    # dataset,features=loaddata()
    # print dataset
    print labels
    labels2 = labels  # 这样的赋值只是引用地址的传递，当labels改变时，labels2也会改变。只有labels2=labels[:]这样的才是真正的拷贝
    tree = createTree(dataset,labels)
    print tree
    # print classify(tree,labels2,[0,1,1,1,0])
    createPlot(tree)
    count = []
    # getCount(tree,dataset,features2,count)
    # print num
    # print count
    # cutBranch_uptodown(tree,dataset,features2)
    cutBranch_downtoup(tree, dataset, labels2, count)
    createPlot(tree)