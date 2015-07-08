#!/usr/bin/env python
# coding: UTF-8
from __future__ import division
from math import sqrt
import numpy
import pylab
from pmpt.hosvd import frobenius_norm, reconstruct, HOSVD, unfold
from pmpt.mobility import init_data, preprocess, trans
from pmpt.util import get_length_height


def oula(vector1, vector2):
    sum = 0
    for i in range(0, len(vector1)):
        sum += pow((vector1[i]-vector2[i]), 2)
    return sqrt(sum)


def recommend(user_unfold, axis_users, users_axis, user_id):
    target_user = users_axis[user_id]
    assert user_unfold.shape[0] == len(users_axis.keys())
    result = []

    for user in range(0, user_unfold.shape[0]):
        if user == target_user:
            continue
        else:
            similarity = oula(user_unfold[target_user], user_unfold[user])
            result.append((axis_users[user], similarity))

    return result

    #
    #
    # user_num = len(A)
    # total = user_num * time_slice
    # availablity = 0
    # sum_precision = 0
    # sum_recall = 0
    # sum_f1_score = 0
    #
    # for user in range(user_num):
    #     for time in range(time_slice):
    #         data = A[user][time]
    #         recom = recommends[user][time]
    #         if recom is None or len(recom) == 0:
    #             continue
    #
    #         availablity += 1
    #         start_set = set()
    #
    #         for item in recom:
    #             if order == 2:
    #                 start_set.add(item[0])
    #             else:
    #                 start_set.add(item[1])
    #
    #         check_list = {}
    #         for item in start_set:
    #             check_list[item] = set()
    #
    #         for item in recom:
    #             if order == 2:
    #                 check_list[item[0]].add(item[1])
    #             else:
    #                 check_list[item[1]].add(item[2])
    #
    #         s_precision = 0
    #         s_recall = 0
    #         s_f1_score = 0
    #         for item in start_set:
    #             recommend_set = set()
    #             pre_data = data[item]
    #             sort_data = []
    #             for index in range(0, len(pre_data)):
    #                 if index in unknow_poi_set[user][time]:
    #                     sort_data.append((index, pre_data[index]))
    #             sort_data.sort(key=lambda x: x[1], reverse=True)
    #             re_sort_data = sort_data[:top_k]
    #             for sort_item in re_sort_data:
    #                 recommend_set.add(sort_item[0])
    #
    #             count_hit = len(recommend_set & check_list[item])
    #
    #             if count_hit == 0:
    #                 precision = 0
    #                 recall = 0
    #                 f1_score = 0
    #             else:
    #                 precision = count_hit / len(recommend_set)
    #                 recall = count_hit / len(check_list[item])
    #                 f1_score = (2 * precision * recall) / (precision + recall)
    #
    #             s_precision += precision
    #             s_recall += recall
    #             s_f1_score += f1_score
    #
    #         # print "precision", s_precision / len(start_set)
    #         sum_precision += s_precision / len(start_set)
    #         sum_recall += s_recall / len(start_set)
    #         sum_f1_score += s_f1_score / len(start_set)
    #
    # return sum_precision / total, sum_recall / total, sum_f1_score / total, availablity / total

# 三个方向优化：
# 1.计算方法的优化： 设计了基于poi集合的转移概率计算
# 2.训练数据的优化： 针对用户访问不同poi数目很少或者某poi被不同的用户访问很少
# 3.hosvd计算的优化： 降低阀值和迭代次数

if __name__ == '__main__':
    time_slice = 2
    train = 0.6
    # beijing = (39.433333, 41.05, 115.416667, 117.5)
    # haidian = (39.883333, 40.15, 116.05, 116.383333)
    # region = (39.88, 40.03, 116.05, 116.25)
    # region = (39.88, 40.05, 116.05, 116.26)
    region = (39.98, 40.02, 116.30, 116.35)
    cluster_radius = 1
    filter_count = 40
    order = 2
    top_k = 1

    length, height, top_left = get_length_height(region)
    print "区域（长度，宽度）：", length, height

    temp_data, time_slice, train, cluster_radius = init_data(time_slice, train, region, cluster_radius, filter_count)

    axis_pois, axis_users, users_axis, train_structure_data, poi_adjacent_list, recommends, unknow_poi_set, poi_num = preprocess(temp_data, time_slice, train, cluster_radius, order, filter_poi=True)
    print "train_structure_data: ", train_structure_data
    print "poi_adjacent_list: ", poi_adjacent_list
    print "recommends: ", recommends

    tensor = trans(train_structure_data, poi_adjacent_list, order, len(axis_pois), len(axis_users), time_slice)
    # print "transition tensor: ", tensor


    U, S, D = HOSVD(numpy.array(tensor), 0.7)

    A = reconstruct(S, U)
    print "reconstruct tensor: ", A
    print frobenius_norm(tensor-A)

    user_unfold = unfold(A, 1)
    print "user_tensor: ", type(A), A.shape, user_unfold, user_unfold[0], user_unfold[1], user_unfold[2]

    print "用户的ID: ", users_axis.keys()
    user_list = recommend(user_unfold, axis_users, users_axis, 9)
    user_list.sort(key=lambda x: x[1], reverse=False)

    print "结果: ", user_list
    # avg_precision, avg_recall, avg_f1_score, availability = recommend(A, recommends, unknow_poi_set, time_slice, top_k, order)
    # print "avg_precision: ", avg_precision
    # print "avg_recall: ", avg_recall
    # print "avg_f1_score: ", avg_f1_score
    # print "availability: ", availability


    # time_slice_range = (1, 2, 4, 6, 12)
    # index = 0

    # x_values = []
    # y_values1 = []
    # y_values2 = []
    # y_values3 = []
    # y_values4 = []
    # while top_k <= 10:
    #     avg_precision, avg_recall, avg_f1_score, availability = recommend(A, recommends, unknow_poi_set, time_slice, top_k, order)
    #     print "avg_precision: ", avg_precision
    #     print "avg_recall: ", avg_recall
    #     print "avg_f1_score: ", avg_f1_score
    #     print "availability: ", availability
    #
    #     y_values1.append(avg_precision)
    #     y_values2.append(avg_recall)
    #     y_values3.append(avg_f1_score)
    #     y_values4.append(availability)
    #     x_values.append(top_k)
    #     top_k += 1
    #
    # pylab.plot(x_values, y_values1, 'rs', linewidth=1, linestyle="-", label=u"准确率")
    # pylab.plot(x_values, y_values2, 'gs', linewidth=1, linestyle="-", label=u"召回率")
    # pylab.plot(x_values, y_values3, 'bs', linewidth=1, linestyle="-", label=u"f1值")
    # pylab.plot(x_values, y_values4, 'ks', linewidth=1, linestyle="-", label=u"可用率")
    # pylab.xlabel(u"top-k的k值")
    # pylab.ylabel(u"准确率-召回率")
    # pylab.title(u"top-k值与准确率-召回率之间的关系")
    # pylab.legend(loc='lower right')
    # pylab.xlim(1, 10)
    # pylab.ylim(0, 1.)
    # pylab.show()