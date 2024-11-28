import pytest

from ..webgal_utils import TEXT_SPLIT_PUNCTUATIONS, text_split_sentence, remove_parathesis

def test_split():
    examples = [
        "你好，我是客服小祥。有什么可以帮忙的吗？",
        "一句话。这句话没有标点",
        "。！？",
        "。！？！",
        "这句话不在。（这句话在括号里。）",
        "这句没有标点不在（这句话在括号里。）", 
        "（这句话在括号里。）这句话不在。",
        "（这句话在括号里没有标点）这句话不在。",
        "（挂断电话后，祥子长舒一口气，脸上的职业假笑瞬间消失。她揉了揉太阳穴，感觉一阵疲惫涌上心头。）",
        "（挂断电话后，祥子长舒一口气，脸上的职业假笑瞬间消失。她揉了",
        "（挂断电话后，祥子长舒一口气，脸上的职业假笑瞬",
        "至于其他安排...（祥子心中闪过一丝疲惫，但随即恢复了坚毅）还是专注于眼前的任务吧，其他的暂时不去想了。"
    ]

    for i_example, example in enumerate(examples):
        split_result = text_split_sentence(example)
        print(i_example, ':', split_result)
        for sent in split_result:
            print('|',remove_parathesis(sent),'|',sep='')

        assert ''.join(split_result) == example