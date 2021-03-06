#!/usr/bin/env python
# coding: UTF-8
from __future__ import division
import numpy
import pylab
from pmpt.build import recommend
from pmpt.hosvd import frobenius_norm, reconstruct, HOSVD
from pmpt.mobility import init_data, preprocess, trans
from pmpt.util import get_length_height
from factorized_markov_chain.mobility import init_data as init_data2, preprocess as preprocess2, trans as trans2
from tensor_factorization.mobility import init_data as init_data3, preprocess as preprocess3, trans as trans3
from factorized_markov_chain.build import recommend as recommend2
from tensor_factorization.build import recommend as recommend3
# 1. 正确率 = 提取出的正确信息条数 /  提取出的信息条数
# 2. 召回率 = 提取出的正确信息条数 /  样本中的信息条数
# 两者取值在0和1之间，数值越接近1，查准率或查全率就越高。
# 3. F值  = 正确率 * 召回率 * 2 / (正确率 + 召回率) （F 值即为正确率和召回率的调和平均值）

# 与state of the art方法进行对比：
# 1.Factorized Markov Chain（FMC）：二阶马尔科夫链进行hosvd分解，没有用户之间和时间之间的信息协同
# 2.Tersor Factorization（TF）：基于用户-时间-地点的频数张量进行hosvd分解，没有用户的转移信息（地点对地点的评分）

if __name__ == '__main__':
    time_slice = 2
    train = 0.5
    # beijing = (39.433333, 41.05, 115.416667, 117.5)
    # haidian = (39.883333, 40.15, 116.05, 116.383333)
    # region = (39.88, 40.03, 116.05, 116.25)
    # region = (39.88, 40.05, 116.05, 116.26)
    region = (39.88, 40.05, 116.05, 116.26)
    cluster_radius = 1
    filter_count = 30
    order = 2
    top_k = 1

    length, height, top_left = get_length_height(region)
    print "区域（长度，宽度）：", length, height

    # pmpt
    temp_data, time_slice, train, cluster_radius = init_data(time_slice, train, region, cluster_radius, filter_count)
    axis_pois, axis_users, train_structure_data, poi_adjacent_list, recommends, unknow_poi_set = preprocess(temp_data, time_slice, train, cluster_radius, order)
    tensor = trans(train_structure_data, poi_adjacent_list, order, len(axis_pois), len(axis_users), time_slice)
    U, S, D = HOSVD(numpy.array(tensor), 0.7)
    A = reconstruct(S, U)

    # factorized markov chain
    temp_data2, time_slice, train2 = init_data2(region, train, time_slice, filter_count)
    axis_pois2, axis_users2, train_structure_data2, recommends2, unknow_poi_set2 = preprocess2(temp_data2, time_slice, train2, order)
    A2 = trans2(train_structure_data2, order, len(axis_pois2), time_slice, 0.7)

    # tensor factorization
    temp_data3, time_slice, train3 = init_data3(time_slice, train, region, filter_count)
    axis_pois3, axis_users3, train_structure_data3, recommends3, unknow_poi_set3 = preprocess3(temp_data3, time_slice, train3, order)
    tensor3 = trans3(train_structure_data3, order, len(axis_pois3), len(axis_users3), time_slice)
    U3, S3, D3 = HOSVD(numpy.array(tensor3), 0.7)
    A3 = reconstruct(S3, U3)

    x_values = []
    y_values1 = []
    y_values2 = []
    y_values3 = []
    y_values4 = []
    while top_k <= 10:
        avg_precision, avg_recall, avg_f1_score, availability = recommend(A, recommends, unknow_poi_set, time_slice, top_k, order)
        print "avg_f1_score(pmpt): ", avg_f1_score

        avg_precision2, avg_recall2, avg_f1_score2, availability2 = recommend2(A2, recommends2, unknow_poi_set2, time_slice, top_k, order)
        print "avg_f1_score(fmc): ", avg_f1_score2

        avg_precision3, avg_recall3, avg_f1_score3, availability3 = recommend3(A3, recommends3, unknow_poi_set3, time_slice, top_k, order)
        print "avg_f1_score(tf): ", avg_f1_score3

        y_values1.append(avg_f1_score)
        y_values2.append(avg_f1_score2)
        y_values3.append(avg_f1_score3)
        # y_values4.append(availability)
        x_values.append(top_k)
        top_k += 1

    pylab.plot(x_values, y_values1, 'ro', linewidth=1.5, linestyle="-", label=u"PMPT")
    pylab.plot(x_values, y_values2, 'go', linewidth=1.5, linestyle="-", label=u"FMC")
    pylab.plot(x_values, y_values3, 'bo', linewidth=1.5, linestyle="-", label=u"TF")
    # pylab.plot(x_values, y_values4, 'ks', linewidth=1, linestyle="-", label=u"可用率")
    pylab.xlabel(u"top-k的k值")
    pylab.ylabel(u"f1值")
    pylab.title(u"PMPT、FMC、TF方法f1值对比(时间维度为2)")
    pylab.legend(loc='center right')
    # pylab.xlim(1, 10)
    # pylab.ylim(0, 1.)
    pylab.show()