#!/usr/bin/env python3
# coding: utf-8
# File: answer_search_KG.py
# Author: heliu
# Date: 2019-09-23

from py2neo import Graph


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",
            http_port=7474,
            user="neo4j",
            password="!@aA123456")
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sqls):
        final_answers = []
        if not sqls:
            return final_answers
        keyword = ' where '
        query = 'match (n:components) '
        dom_classify = False
        for sql_ in sqls:
            if sql_['question_type'] == 'dom_classify_components':
                dom_classify = True
            elif '###' not in sql_['question_type']:
                query += (', ' + sql_['sql'][0])
            else:
                query += (keyword + sql_['sql'][0])
                keyword = ' and '
        query += ' return n.name, n.type'

        if dom_classify:
            if 'where' in query:
                insert_pos = query.index('where')
            else:
                insert_pos = query.index('return')

            answers = self.g.run(query[:insert_pos] +
                                 ',(n)-[:rels_component_city]->(city:components_city {China: true}) ' +
                                 query[insert_pos:]).data()
            final_answer = self.answer_prettify("classify_domT", answers)
            final_answers.append(final_answer)

            answers = self.g.run(query[:insert_pos] +
                                 ',(n)-[:rels_component_city]->(city:components_city {China: false}) ' +
                                 query[insert_pos:]).data()
            final_answer = self.answer_prettify("classify_domF", answers)
            final_answers.append(final_answer)
        else:
            answers = self.g.run(query).data()
            final_answer = self.answer_prettify("search", answers)
            final_answers.append(final_answer)

        # for sql_ in sqls:
        #     question_type = sql_['question_type']
        #     queries = sql_['sql']
        #     answers = []
        #     for query in queries:
        #         ress = self.g.run(query).data()
        #         answers += ress
        #     ############################################heliu add
        #     # 如果答案不唯一，进一步轮询
        #     # if len(answers) > 1:
        #
        #     ########################################################
        #     # print(answers)
        #     final_answer = self.answer_prettify(question_type, answers)
        #     if final_answer:
        #         final_answers.append(final_answer)

        return final_answers  # , answers

    '''根据对应的qustion_type，调用相应的回复模板'''

    def answer_prettify(self, question_type, answers):
        final_answer = ''
        b_more_question = False
        if not answers:
            return ''
        if question_type == 'search' or question_type[:8] == 'classify':
            if question_type[-1] == 'F':
                final_answer = '进口的'
            elif question_type[-1] == 'T':
                final_answer = '国产的'
            else:
                final_answer = '您要找的'

            final_answer += '型号如下：\n'
            count = 0
            for answer in answers:
                count += 1
                final_answer += "%s. 型号：%s 名称：%s\n" %(count, answer['n.type'], answer['n.name'])
        if question_type == 'weapons_description':
            desc = [i['m.desc'] for i in answers]
            subject = answers[0]['m.name']
            max_V = answers[0]['m.max_V']
            max_L = answers[0]['m.max_L']
            # final_answer = '{0}的简介：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
            final_answer = '{0}的简介：{1}最大速度：{2}\n最大航程：{3}'.format(subject, '；'.join(list(set(desc)))[:], max_V, max_L)
            # final_answer = '{0}的简介：{1}\n最大速度：{2}\n最大航程：{3}'.format(subject, set(desc), max_V, max_L)

        elif question_type == 'weapon_times':
            # desc = [i['m.name'] for i in answers]
            subject = answers[0]['m.name']
            time = answers[0]['n.name']
            final_answer = '{0}的首发时间为：{1}'.format(subject, time)

        elif question_type == 'weapon_sites':
            subject = answers[0]['m.name']
            site = answers[0]['n.name']
            final_answer = '{0}的产国为：{1}'.format(subject, site)

        elif question_type == 'weapon_organizations':
            subject = answers[0]['m.name']
            org = answers[0]['n.name']
            final_answer = '{0}的生产商为：{1}'.format(subject, org)

        elif question_type == 'weapon_types':
            subject = answers[0]['m.name']
            cats = answers[0]['n.name']
            final_answer = '{0}的类型为：{1}'.format(subject, cats)

        elif question_type == 'system_fault_deal':
            subject = []
            for answer in answers:
                subject.append(answer['n.name'])

            # subject = answers[0]['n.name']
            # subject = answers[0]['m.name']
            # cats = answers[0]['n.name']
            final_answer = '本系统包含的部件有：{0}，分析是否有故障发生'.format(subject)

        elif question_type == 'fault_deal':
            subject = []
            if len(answers) > 1:
                for answer in answers:
                    subject.append(answer['m.name'])

                # subject = answers[0]['n.name']
                # subject = answers[0]['m.name']
                # cats = answers[0]['n.name']
                final_answer = '发生过此类故障的部件有：{0}，请问是哪个部件发生的故障？'.format(subject)
            elif len(answers) == 1:
                subject = answers[0]['m.name']
                final_answer = '发生过此类故障的部件为：{0}。'.format(subject)

        elif question_type == 'unit_comCats_search':
            subject = []
            for answer in answers:
                subject.append(answer['n.name'])
            final_answer = '此部件包含的元器件有：{0}。'.format(subject)

        elif question_type == 'comCats_malfunction_search':
            subject = []
            for answer in answers:
                subject.append(answer['n.name'])
            final_answer = '发生过的故障有：{0}。'.format(subject)

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()
