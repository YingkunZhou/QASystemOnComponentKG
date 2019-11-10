#!/usr/bin/env python3
# coding: utf-8
# File: chatbot_graph.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4

from question_classifier_KG import *
from question_parser_KG import *
from answer_search_KG import *

'''问答类'''


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        default = '您好，我是人工智能副官-贾维斯，希望可以帮到您。'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return default
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return default
        else:
            return_result = '\n'.join(final_answers)
            if not return_result:
                return '非常抱歉，没有找到'
            else:
                return return_result
        # final_answers = []
        # question_count = 0
        # while ('本问题结束' not in sent) and (question_count < 1):
        #     res_classify = self.classifier.classify(sent)
        #     if not res_classify:
        #         return answer
        #     elif res_classify['question_types'] == ['fault_deal']:
        #         entity_dict = self.parser.build_entitydict(res_classify['args'])
        #         fault_ques = entity_dict.get('malfunctions_entity')  # fault_ques中为['显示器黑屏']
        #         res_sql = self.parser.parser_main(res_classify)
        #         sent, answers_tmp = self.searcher.search_main(res_sql)
        #         print('贾维斯:', sent)
        #         fault_unit_user_choose = input('用户:')
        #         fault_unit_ques = fault_unit_user_choose + fault_ques[0] + '如何处理'
        #         res_classify = self.classifier.classify(fault_unit_ques)
        #         if not res_classify:
        #             return answer
        #         res_sql = self.parser.parser_main(res_classify)
        #         sent, answers_tmp = self.searcher.search_main(res_sql)
        #
        #         final_answers += sent
        #
        #         # 在得到故障部件后，查找故障部件包含的元器件
        #         unit_comCats_ques = fault_unit_user_choose + '包含的元器件有哪些'
        #         res_classify = self.classifier.classify(unit_comCats_ques)
        #         if not res_classify:
        #             return answer
        #         res_sql = self.parser.parser_main(res_classify)
        #         sent, answers_tmp = self.searcher.search_main(res_sql)
        #         final_answers += sent
        #         tmp_comFinalanswer = ""
        #         for answer in answers_tmp:
        #             # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        #             # print(answer)
        #             comCats_fault_ques = answer.get('n.name') + '包含的故障有哪些'
        #             res_classify = self.classifier.classify(comCats_fault_ques)
        #             if not res_classify:
        #                 return answer
        #             res_sql = self.parser.parser_main(res_classify)
        #             tem_sent, answers_tmp = self.searcher.search_main(res_sql)
        #
        #             sent = [answer.get('n.name') + tem_sent[0]]
        #             # print(answers_tmp)
        #             # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        #             # print(sent)
        #             # sent = answer.get('n.name') + tem_sent
        #             # print(sent)
        #             final_answers += sent
        #             # tmp_comFinalanswer = ""
        #             for tmp_fanswer in answers_tmp:
        #                 tmp_comFinalanswer += tmp_fanswer.get('n.name') + "、"
        #             # print(type(tmp_comFinalanswer))
        #             # print(type(fault_ques))
        #             # tmp_comFinalanswer = tmp_comFinalanswer[:-1]
        #             # final_answers += ["元器件的故障："+ tmp_comFinalanswer+"，可能导致您的部件故障--"+fault_ques[0]]
        #
        #         # print(sent)
        #
        #     # print("res_sql:")
        #     # print(res_sql)
        #
        #     # final_answers += sent
        #
        #     # print("final_answers")
        #     # print(final_answers)
        #     question_count += 1
        #     tmp_comFinalanswer = tmp_comFinalanswer[:-1]
        #     final_answers += ["元器件的故障：" + tmp_comFinalanswer + "，可能导致您的部件故障--" + fault_ques[0]]
        #     final_answers += ["\n希望贾维斯可以帮到您！"]
        #
        # if not final_answers:
        #     return answer
        # else:
        #     return '\n'.join(final_answers)


if __name__ == '__main__':
    handler = ChatBotGraph()
    print('您好，我是人工智能副官-贾维斯，希望可以帮到您。')
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('贾维斯:', answer)
