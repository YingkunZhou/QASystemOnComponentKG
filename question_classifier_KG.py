#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

import os
import ahocorasick
import re
import jieba
import jieba.posseg as pseg
from build_Neo4j import transfer

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        jieba.load_userdict("user_dict.txt")

        #　特征词路径
        #weapon相关特征词
        self.weapons_entity_path = os.path.join(cur_dir, 'dict/weapons_entity.txt')
        self.weapons_cats_path = os.path.join(cur_dir, 'dict/weapons_cats.txt')
        self.weapons_organizations_path = os.path.join(cur_dir, 'dict/weapons_organizations.txt')
        self.weapons_country_path = os.path.join(cur_dir, 'dict/weapons_country.txt')
        self.weapons_types_path = os.path.join(cur_dir, 'dict/weapons_types.txt')
        #component相关特征词
        self.components_cats_path = os.path.join(cur_dir, 'dict/components_cats.txt')
        self.components_entity_path = os.path.join(cur_dir, 'dict/components_entity.txt')
        self.components_city_path = os.path.join(cur_dir, 'dict/components_city.txt')
        self.components_organizations_path = os.path.join(cur_dir, 'dict/components_organizations.txt')
        #fault相关特征词
        self.units_entity_path = os.path.join(cur_dir, 'dict/units_entity.txt')
        self.systems_entity_path = os.path.join(cur_dir, 'dict/systems_entity.txt')
        self.malfunctions_entity_path = os.path.join(cur_dir, 'dict/malfunctions_entity.txt')

        # 加载特征词
        #weapon类特征词
        self.weapons_entity_wds= [i.strip() for i in open(self.weapons_entity_path, encoding='UTF-8') if i.strip()]
        self.weapons_cats_wds= [i.strip() for i in open(self.weapons_cats_path, encoding='UTF-8') if i.strip()]
        self.weapons_organizations_wds= [i.strip() for i in open(self.weapons_organizations_path, encoding='UTF-8') if i.strip()]
        self.weapons_country_wds= [i.strip() for i in open(self.weapons_country_path, encoding='UTF-8') if i.strip()]
        self.weapons_types_wds= [i.strip() for i in open(self.weapons_types_path, encoding='UTF-8') if i.strip()]
        # self.region_words_tmp += self.weapons_entity_wds + self.weapons_cats_wds + self.weapons_organizations_wds + self.weapons_country_wds + self.weapons_types_wds
        #component类特征词
        self.components_cats_wds = [i.strip() for i in open(self.components_cats_path, encoding='UTF-8') if i.strip()]
        self.components_entity_wds = [i.strip() for i in open(self.components_entity_path, encoding='UTF-8') if i.strip()]
        self.components_city_wds = [i.strip() for i in open(self.components_city_path, encoding='UTF-8') if i.strip()]
        self.components_organizations_wds = [i.strip() for i in open(self.components_organizations_path, encoding='UTF-8') if i.strip()]
        self.region_words_tmp = self.components_cats_wds + self.components_entity_wds + self.components_city_wds + self.components_organizations_wds
        #fault类特征词
        self.units_entity_wds = [i.strip() for i in open(self.units_entity_path, encoding='UTF-8') if i.strip()]
        self.systems_entity_wds = [i.strip() for i in open(self.systems_entity_path, encoding='UTF-8') if i.strip()]
        self.malfunctions_entity_wds = [i.strip() for i in open(self.malfunctions_entity_path, encoding='UTF-8') if i.strip()]
        # self.region_words_tmp += self.units_entity_wds + self.systems_entity_wds + self.malfunctions_entity_wds
        self.region_words = set(self.region_words_tmp)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.weapons_entity_qwds = ['武器型号', '飞机型号', '武器', '飞机']
        self.weapons_country_qwds = ['产国','产于', '哪里生产', '生产', '产地']
        self.weapons_organizations_qwds = ['产商', '生产厂商', '生产机构', '生产商']
        self.weapons_types_qwds = ['类别', '类型']
        self.fault_deal_qwds = ['处理措施', '如何处理', '怎么办', '怎么处理']#处理措施的问句
        self.unit_has_comCats_qwds = ['包含的元器件', '含有什么元器件', '具有哪些元器件']
        self.comCats_has_fault_qwds = ['包含的故障', '含有什么故障', '发生过哪些故障']

        self.search_components = ['哪些']
        self.classify_components = ['分类']
        self.components_property = ['name', 'type', 'quality', 'encap_mode',
                                    'power', 'tmp_char', 'tmp', 'weight', 'res', 'size']
        self.cpt_string_property = ['name', 'type', 'quality', 'encap_mode']
        self.op_dict = {'a': '<', 'b': '<=', 'c': '=', 'd': '>', 'e': '>='}
        # self.components_power = ['额定功耗', '功耗']
        # self.components_tmper = ['温度']
        # self.components_quality = ['质量等级']
        # self.components_weight = ['重量', '质量']
        # self.components_property = self.components_power + self.components_tmper + \
        #                            self.components_quality + self.components_weight
        #
        # self.compare_range = ['范围']
        # self.compare_less = ['小于', '低于', '以下']
        # self.compare_less_equal = ['不超过', '不大于', '不高于']
        # self.compare_equal = ['等于', '为']
        # self.compare_greater = ['大于', '超过', '高于', '以上']
        # self.compare_greater_equal = ['不小于', '不低于']
        # self.compare_include = ['包含']
        # self.compare_within = ['之间']

        print('model init finished ......')

        return

    '''分类主函数'''
    def classify(self, question):
        data = {}
        entity_dict = self.check_entity(question)
        #print(entity_dict)
        # if not entity_dict:
        #     return {}
        data['args'] = entity_dict
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in entity_dict.values():
            types += type_

        question_types = []

        if self.check_words(self.search_components, question) or self.check_words(self.classify_components, question):
            '''here we deal with relationship'''
            if 'components_cats' in types:
                question_type = 'cats_search_components'  # 问句类型为系统故障处理措施
                question_types.append(question_type)
            if 'components_city' in types:
                question_type = 'city_search_components'  # 问句类型为系统故障处理措施
                question_types.append(question_type)
            if 'components_organizations' in types:
                question_type = 'org_search_components'  # 问句类型为系统故障处理措施
                question_types.append(question_type)

            if self.check_words(self.classify_components, question):
                if '进口' in question and '国产' in question:
                    question_type = 'dom_classify_components'
                    question_types.append(question_type)
            else:
                if '国产' in question:
                    question_type = 'dom_search_components-->true'
                    question_types.append(question_type)
                if '进口' in question:
                    question_type = 'dom_search_components-->false'
                    question_types.append(question_type)

            result = pseg.cut(question)
            seg_words = [w.word for w in result]
            if '电阻' in seg_words:
                question_type = 'type_search_components-->电阻'
                question_types.append(question_type)
            if '振荡器' in seg_words:
                question_type = 'type_search_components-->振荡器'
                question_types.append(question_type)

            '''here we deal with properties'''
            result = pseg.cut(question)
            scan_property = {}
            prev_word = ''
            prev_flag = ''
            for w in result:
                if prev_flag == 'm':
                    ratio = transfer(w.word)
                    scan_property['value'] = ratio * scan_property['value']
                    if 'value2' in scan_property:
                        scan_property['value2'] = ratio * scan_property['value2']

                if 'key' in scan_property and 'op' in scan_property and 'value' in scan_property:
                    question_type = ''
                    key = scan_property['key']
                    op = scan_property['op']
                    if key == 'tmp' or key == 'res':
                        if op == '=':
                            question_type = '%s_lower###%s###%s###%s_upper###%s###%s' % \
                                            (key, '=', scan_property['value'],
                                             key, '=', scan_property['value2'])
                        elif op[0] == '>':
                            question_type = '%s_lower###%s###%s' % (key, op, scan_property['value'])
                        elif op[0] == '<':
                            question_type = '%s_upper###%s###%s' % (key, op, scan_property['value'])
                    else:
                        question_type = '%s###%s###%s' % (key, op, scan_property['value'])
                    question_types.append(question_type)
                    scan_property.clear()
                elif 'key' in scan_property and 'op1' in scan_property and 'value2' in scan_property:
                    question_type = '%s_lower###%s###%s###%s_upper###%s###%s' % \
                                    (scan_property['key'], scan_property['op1'], scan_property['value'],
                                     scan_property['key'], scan_property['op2'], scan_property['value2'])
                    question_types.append(question_type)
                    scan_property.clear()

                if w.flag in self.components_property:
                    scan_property['key'] = w.flag
                elif w.flag[:2] == 'op':
                    op = w.flag[2]
                    if op < 'f' and 'op1' not in scan_property:
                        if prev_flag == 'opf' and op == 'c':  # 范围为/范围是/范围等于。。。
                            scan_property['op1'] = '='
                            scan_property['op2'] = '='
                        else:
                            scan_property['op'] = self.op_dict[op]
                    # elif op == 'f': # 范围
                    #     scan_property['op1'] = '='
                    #     scan_property['op2'] = '='
                    elif op == 'g': # 包含
                        scan_property['op1'] = '<='
                        scan_property['op2'] = '>='
                    elif op == 'h': # 之间
                        scan_property['op1'] = '>='
                        scan_property['op2'] = '<='
                elif w.flag[0] == 'v' and w.flag[1:] in self.cpt_string_property:
                    scan_property['value'] = "'%s'" % w.word  # string type
                elif w.flag == 'm':
                    value = float(w.word)
                    if prev_word == '-':
                        value = -1 * value

                    if 'value' in scan_property:
                        scan_property['value2'] = value
                    else:
                        scan_property['value'] = value

                prev_word = w.word
                prev_flag = w.flag
        '''
        # 武器描述
        if self.check_words(self.weapons_entity_qwds, question) and ('weapons_entity' in types):
            question_type = 'weapons_description'
            question_types.append(question_type)

        # 武器首发时间
        if self.check_words(self.weapon_times_qwds, question) and ('weapons_entity' in types):
            question_type = 'weapon_times'
            question_types.append(question_type)

        # 武器产国
        if self.check_words(self.madecountry_qwds, question) and ('weapons_entity' in types):
            question_type = 'weapon_sites'
            question_types.append(question_type)

        # 武器产商
        if self.check_words(self.madeorg_qwds, question) and ('weapons_entity' in types):
            question_type = 'weapon_organizations'
            question_types.append(question_type)

        # 武器类型
        if self.check_words(self.weapon_types_qwds, question) and ('weapons_entity' in types):
            print("heliu1#####################################")
            question_type = 'weapon_types'
            question_types.append(question_type)
        '''

        # #故障解决方案，问句中包含系统实体+故障实体+处理措施关键词
        # if self.check_words(self.fault_deal_qwds, question) and ('systems_entity' in types) and ('malfunctions_entity' in types):
        #     question_type = 'system_fault_deal'#问句类型为系统故障处理措施
        #     question_types.append(question_type)
        #
        # #故障解决方案，问句中只含有故障现象，没有故障发生的实体
        # if self.check_words(self.fault_deal_qwds, question) and ('units_entity' not in types) and ('malfunctions_entity' in types):
        #     question_type = 'fault_deal'#问句类型为故障-处理措施
        #     question_types.append(question_type)
        #
        # #问句中含有部件实体+故障实体+解决方案关键词
        # if self.check_words(self.fault_deal_qwds, question) and ('units_entity' in types) and ('malfunctions_entity' in types):
        #     question_type = 'unit_fault_deal'#问句类型为部件实体-故障-处理措施
        #     question_types.append(question_type)
        #
        # #问句中含有部件实体+包含元器件关键词，搜索类型为查找部件实体包含的元器件
        # if self.check_words(self.unit_has_comCats_qwds, question) and ('units_entity' in types):
        #     question_type = 'unit_comCats_search'#问句类型为通过部件实体搜索包含的元器件
        #     question_types.append(question_type)
        #
        # # 问句中含有部件实体+包含元器件关键词，搜索类型为查找部件实体包含的元器件
        # if self.check_words(self.comCats_has_fault_qwds, question) and ('components_cats' in types):
        #     question_type = 'comCats_malfunction_search'  # 问句类型为通过元器件类型实体搜索包含的故障
        #     question_types.append(question_type)



        # 若没有查到相关的外部查询信息，那么则将该武器的描述信息返回
        #if question_types == [] and 'weapons_entity' in types:
        #    question_types = ['weapons_description']

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = question_types

        return data

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            #weapon相关的构造词
            if wd in self.weapons_entity_wds:
                wd_dict[wd].append('weapons_entity')
            if wd in self.weapons_cats_wds:
                wd_dict[wd].append('weapons_cats')
            if wd in self.weapons_organizations_wds:
                wd_dict[wd].append('weapons_organizations')
            if wd in self.weapons_country_wds:
                wd_dict[wd].append('weapons_country')
            if wd in self.weapons_types_wds:
                wd_dict[wd].append('weapons_types')
            #component相关的构造词
            if wd in self.components_cats_wds:
                wd_dict[wd].append('components_cats')
            if wd in self.components_entity_wds:
                wd_dict[wd].append('components_entity')
            if wd in self.components_city_wds:
                wd_dict[wd].append('components_city')
            if wd in self.components_organizations_wds:
                wd_dict[wd].append('components_organizations')

            #fault相关的构造词
            if wd in self.units_entity_wds:
                wd_dict[wd].append('units_entity')
            if wd in self.systems_entity_wds:
                wd_dict[wd].append('systems_entity')
            if wd in self.malfunctions_entity_wds:
                wd_dict[wd].append('malfunctions_entity')

        return wd_dict

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        #print(actree)
        return actree

    '''问句过滤'''
    def check_entity(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}
        return final_dict

    '''基于特征词进行分类'''
    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False

    def operator(self, word):
        op = ''
        if word in self.compare_less:
            op = '<'
        if word in self.compare_less_equal:
            op = '<='
        if word in self.compare_equal:
            op = '='
        if word in self.compare_greater:
            op = '>'
        if word in self.compare_greater_equal:
            op = '>='
        return op

if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('input an question:')
        data = handler.classify(question)
        #print(data)