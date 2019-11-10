#!/usr/bin/env python3
# coding: utf-8
# File: question_parser.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

from answer_search_KG import *

class QuestionPaser:

    def __init__(self):
        self.searcher = AnswerSearcher()

    '''构建实体节点'''
    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            #print(args.items())
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)
        return entity_dict

    '''解析主函数'''
    def parser_main(self, res_classify):
        args = res_classify['args']
        #print("heliu@@@@@@@@@@@@@@@@@@@@@@")
        #print(args)
        entity_dict = self.build_entitydict(args)
        #print("heliu%%%%%%%%%%%%%%%%%%%%%%%%%%")
        #print(entity_dict)
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if 'classify' in question_type:
                sql = [question_type]  # FIXME:useless, can store other information maybe
            # '''deal with property'''
            elif '###' in question_type:
                pair = question_type.split('###')
                if len(pair) == 3:
                    sql = ["n.%s %s %s" % (pair[0], pair[1], pair[2])]
                else:
                    sql = ["n.%s %s %s and n.%s %s %s" % (pair[0], pair[1], pair[2], pair[3], pair[4], pair[5])]
            # '''deal with relationship'''
            elif '-->' in question_type:
                pair = question_type.split('-->')
                if pair[0] == 'dom_search_components':
                    sql = ["(n)-[:rels_component_city]->(city:components_city {China: %s})" % pair[1]]
                elif pair[0] == 'type_search_components':
                    sql = ["(n)-[:rels_component_comCats]->(cat:components_cats {type:'%s'})" % pair[1]]

            elif question_type == 'cats_search_components':
                label = 'components_cats'
                sql = ["(n)-[:rels_component_comCats]->(cat:%s {name:'%s'})" % (label, entity_dict.get(label)[0])]
            elif question_type == 'city_search_components':
                label = 'components_city'
                sql = ["(n)-[:rels_component_city]->(city:%s {name: '%s'})" % (label, entity_dict.get(label)[0])]
            elif question_type == 'org_search_components':
                label = 'components_organizations'
                sql = ["(n)-[:rels_component_organization]->(org:%s {name: '%s'})" % (label, entity_dict.get(label)[0])]

            # if question_type == 'weapons_description':
            #     sql = self.sql_transfer(question_type, entity_dict.get('weapons'))
            #
            # elif question_type == 'weapon_times':
            #     sql = self.sql_transfer(question_type, entity_dict.get('weapons'))
            #
            # elif question_type == 'weapon_sites':
            #     sql = self.sql_transfer(question_type, entity_dict.get('weapons'))
            #
            # elif question_type == 'weapon_organizations':
            #     sql = self.sql_transfer(question_type, entity_dict.get('weapons'))
            #
            # elif question_type == 'weapon_types':
            #     sql = self.sql_transfer(question_type, entity_dict.get('weapons'))
            #
            # elif question_type == 'system_fault_deal':
            #     sql = self.sql_transfer(question_type, entity_dict.get('systems_entity'))
            #
            # elif question_type == 'fault_deal':#如果输入的问题是故障-处理措施类型，返回有此故障的设备
            #     sql = self.sql_transfer(question_type, entity_dict.get('malfunctions_entity'))
            #
            # elif question_type == 'unit_fault_deal':#如果输入的问题是部件实体-故障-处理措施类型，返回部件+故障实体共同指向的解决方案
            #     sql = self.sql_transfer(question_type, entity_dict.get('units_entity')+entity_dict.get('malfunctions_entity'))
            #
            # elif question_type == 'unit_comCats_search':#如果输入的问题是故障-处理措施类型，返回有此故障的设备
            #     sql = self.sql_transfer(question_type, entity_dict.get('units_entity'))
            #
            # elif question_type == 'comCats_malfunction_search':#如果输入的问题是故障-处理措施类型，返回有此故障的设备
            #     sql = self.sql_transfer(question_type, entity_dict.get('components_cats'))

            if sql:
                sql_['sql'] = sql

                sqls.append(sql_)

        return sqls

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []
        # 查询武器信息
        if question_type == 'weapons_description':
            sql = ["MATCH (m:weapons) where m.name = '{0}' return m.name, m.desc, m.max_V, m.max_L".format(i) for i in entities]

        # 查询武器首发时间
        elif question_type == 'weapon_times':
            sql = ["MATCH (m:weapons)-[r:first_time_use]->(n:weapon_times) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询武器产国
        elif question_type == 'weapon_sites':
            sql = ["MATCH (m:weapons)-[r:weapon_country]->(n:weapon_sites) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询武器产商
        elif question_type == 'weapon_organizations':
            sql = ["MATCH (m:weapons)-[r:weapon_organization]->(n:weapon_organizations) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        # 查询武器类型
        elif question_type == 'weapon_types':
            sql = ["MATCH (m:weapons)-[r:belongs_to]->(n:weapon_types) where m.name = '{0}' return m.name, r.name, n.name".format(i) for i in entities]

        elif question_type == 'system_fault_deal':
            sql = ["MATCH (m:systems_entity)-[r:rels_system_unit]->(n:units_entity) where m.name = '{0}' return n.name".format(i) for i in entities]

        elif question_type == 'fault_deal':
            sql = ["MATCH (m:units_entity)-[r:rels_unit_fault]->(n:malfunctions_entity) where n.name = '{0}' return m.name".format(i) for i in entities]

        elif question_type == 'unit_fault_deal':
            sql = ["MATCH (m:units_entity)-[r:rels_fault_deal]->(n:faultDeal_entity) where m.name = '{0}' and r.name = '{1}' return m.name".format(entities[0], entities[1])]

        elif question_type == 'unit_comCats_search':
            sql = ["MATCH (m:units_entity)-[r:rels_unit_comCats]->(n:components_cats) where m.name = '{0}' return n.name".format(i) for i in entities]

        elif question_type == 'comCats_malfunction_search':
            sql = ["MATCH (m:components_cats)-[r:rels_comCats_malfunction]->(n:malfunctions_entity) where m.name = '{0}' return n.name".format(i) for i in entities]

        #elif question_type == 'unit_comCats_search':
            #sql = ["MATCH (m:units_entity)-[r:rels_unit_comCats]->(n:components_cats) where m.name = '{0}' return n.name".format(i) for i in entities]

        return sql



if __name__ == '__main__':
    handler = QuestionPaser()
