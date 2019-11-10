#encoding=utf-8
# from __future__ import print_function, unicode_literals
import jieba
import jieba.posseg as pseg
# jieba.del_word('小于')
# jieba.del_word('大于')
jieba.load_userdict("user_dict.txt")
# jieba.load_userdict("dict/components_cats.txt")
# jieba.load_userdict("dict/components_city.txt")
# jieba.load_userdict("dict/components_entity.txt")
# jieba.load_userdict("dict/components_organizations.txt")

# jieba.add_word('石墨烯')
# jieba.add_word('凱特琳')
# jieba.del_word('自定义词')

test_sent = (
# "李小福是创新办主任也是云计算方面的专家; 什么是八一双鹿\n"
# "例如我输入一个带“韩玉赏鉴”的标题，在自定义词库中也增加了此词为N类\n"
# "「台中」正確應該不會被切開。mac上可分出「石墨烯」；此時又可以分出來凱特琳了。"
"额定功耗不大于0.25W的在贵州贵阳生产的氧化膜电阻器有哪些\n"
"温度范围可包含-50～150℃的陕西西安生产的射频同轴电连接器有哪些。\n"
"温度范围在-100～150℃之间的陕西西安生产的射频同轴电连接器有哪些。\n"
"温度范围在-40.25~120℃之间的国产振荡器有哪些？\n"
"质量等级为gjb级，质量小于500g的元器件有哪些？\n"
"电阻值大于x，尺寸小于y的电阻有哪些？"
)
words = jieba.cut(test_sent)
print('/'.join(words))

print("="*40)

result = pseg.cut(test_sent)

for w in result:
    print(w.word, "/", w.flag, ", ", end=' ')
#
# print("\n" + "="*40)
#
# terms = jieba.cut('easy_install is great')
# print('/'.join(terms))
# terms = jieba.cut('python 的正则表达式是好用的')
# print('/'.join(terms))
#
# print("="*40)
# # test frequency tune
# testlist = [
# ('今天天气不错', ('今天', '天气')),
# ('如果放到post中将出错。', ('中', '将')),
# ('我们中出了一个叛徒', ('中', '出')),
# ]
#
# for sent, seg in testlist:
#     print('/'.join(jieba.cut(sent, HMM=False)))
#     word = ''.join(seg)
#     print('%s Before: %s, After: %s' % (word, jieba.get_FREQ(word), jieba.suggest_freq(seg, True)))
#     print('/'.join(jieba.cut(sent, HMM=False)))
#     print("-"*40)
