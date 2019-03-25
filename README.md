# Overview
自然言語処理関連の分析でよく行う処理をパッケージ化したもの

# Requirements

* Python (>= 3.4)

# Setting up
* 「mecab」と「swig」がインストールされている必要あり
* 参照辞書にneologdを利用する場合は、「neologd」もインストール

## mecab auto-install
```
make install_mecab
```

## mecab-neologd auto-install
```
make install_neologd
```

## swig auto-install
mecab-python3が0.996.1にアップグレードすると「swig」が必要になる。

```
make install_swig
```

## install
```
pip install git+https://github.com/9en/ToolsNLP
```

# Usage
## Class MecabWrapper
```
>>> import ToolsNLP
>>> text = '稲垣吾郎さん、草彅剛さん、香取慎吾さんの3人によるレギュラー番組 『7.2 新しい別の窓』や『オオカミくんには騙されない』'
>>>
>>> m = ToolsNLP.MecabWrapper(dicttype='neologd')
>>> m.tokenize(sentence=text)
'稲垣吾郎 さん 、 草彅剛 さん 、 香取慎吾 さん の 3人 による レギュラー番組 『 7 . 2 新しい別の窓 』 や 『 オオカミ くん に は 騙す れる ない 』'
>>>
```

## Class TopicModelWrapper
```
>>> import ToolsNLP
>>> data = [i.strip('\n').split('\t') for i in open('data.tsv', 'r')]
>>> # data[:1] output:[['http://news.livedoor.com/article/detail/4778030/', '友人代表のスピーチ、独女はどうこなしている？ ...]]
>>> 
>>> t = ToolsNLP.TopicModelWrapper(data=data, config_mw={'dicttype':'neologd'})
read data ...
documents count => 5,980
tokenize text ...
make corpus ...
all token count => 24,220
topic count => 100
make topic model ...
make output data ...
DONE
>>> 
>>> t.get_topic2topdoc_list().head()
topic                                               url    weight
103      84  http://news.livedoor.com/article/detail/5022412/  0.973764
274      84  http://news.livedoor.com/article/detail/5476676/  0.963469
1149     84  http://news.livedoor.com/article/detail/6468311/  0.955912
1197     84  http://news.livedoor.com/article/detail/6505621/  0.945417
1022     84  http://news.livedoor.com/article/detail/6374433/  0.910676
>>> 
>>> t.get_topic2doccnt_plot()
```

![c9618080-08f9-11e9-967e-46dd32813def](https://user-images.githubusercontent.com/23630426/54873575-2d71e300-4e1c-11e9-90d5-d9407bdc2041.png)

```
>>> 
>>> t.get_topic2term_plot()
```

!![1ba2a180-08fa-11e9-8f21-d3bc7448e319](https://user-images.githubusercontent.com/23630426/54873577-319e0080-4e1c-11e9-93be-5579de1abcaf.png)

![16dded80-08fa-11e9-8fd3-683f4c109e95](https://user-images.githubusercontent.com/23630426/54873580-3793e180-4e1c-11e9-8232-261f5df73888.png)


# Detaile
* [Class MecabWrapper](https://github.com/9en/ToolsNLP/wiki/Class-MecabWrapper)

* [Class TopicModelWrapper](https://github.com/9en/ToolsNLP/wiki/Class-TopicModelWrapper)
