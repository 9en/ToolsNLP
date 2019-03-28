#! -*- coding: utf-8 -*-

import ToolsNLP
import gensim
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import re
import site
import os


class TopicModelWrapper:
    '''
    Description::
        トピックモデルを実行する
    
    :param data:
        入力データ
        [[entry_id1, sentence1], [entry_id2, sentence2], ]
    :param config_mw:
        MecabWrapperのパラメータを設定
        デフォルト設定
            config_mw = {
                        'dicttype':'ipadic'
                        ,'userdict': ''
                        ,'stopword': ''
                        }
    :param config_tn:
        MecabWrapper.tokenizeのパラメータを設定
        デフォルト設定
            config_tn = {
                        'pos_filter': [['名詞', '一般', '*']]
                        ,'is_normalized': True
                        ,'is_org': True
                        ,'is_pos': False
                        }
    :param kwargs:
        トピックモデルの設定
        デフォルト設定
            kwargs = {
                    # 基本設定
                    'stop_term_toprate': 0.05
                    ,'stop_term_limitcnt': 3
                    ,'topic_doc_threshold': 0.01
                    # コーパス設定
                    ,'is_1len': True
                    ,'is_term_fq': True
                    # LDA設定
                    ,'num_topics': 100
                    ,'iterations': 100
                    ,'alpha': 'auto'
                    }

            # 基本設定(stop_term_toprate = 単語出現頻度上位n％を除外する
                    ,stop_term_limitcnt = 単語頻度がn以下を除外する
                    ,topic_doc_threshold = トピックに対して紐づけるドキュメントのスコアの閾値)
            # コーパス設定(is_1len = 形態素解析後の英数字の文字列が1のものを除外するかどうか
                    ,is_term_fq = 単語出現頻度のフィルタを実施するかどうか)
            # LDA設定(num_topics = トピック数
                    ,iterations = イテレーション回数
                    ,alpha = アルファの設定)
    Usage::
        >>> import ToolsNLP
        # doctest用にエスケースしている。元のコード `data = [i.strip('\n').split('\t') for i in open('data.tsv', 'r')]`
        >>> data = [i.strip('\\n').split('\\t') for i in open('data.tsv', 'r')]
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
    '''
    def __init__(self, data, config_mw={}, config_tn={}, **kwargs):
        sitedir = site.getsitepackages()[-1]
        installdir = os.path.join(sitedir, 'ToolsNLP')
        self._fpath = installdir +  '/.fonts/ipaexg.ttf'
        # 基本設定
        self._stop_term_limitcnt = kwargs.get('stop_term_limitcnt', 3)
        self._topic_doc_threshold = kwargs.get('topic_doc_threshold', 0.01)
        # コーパス設定
        self._is_1len = kwargs.get('is_1len', True)
        self._is_term_fq = kwargs.get('is_term_fq', True)
        # LDA設定
        self._num_topics = kwargs.get('num_topics', 100)
        self._iterations = kwargs.get('iterations', 100)
        self._alpha = kwargs.get('alpha', 'auto')
        # 形態素解析設定
        self._config_mw = config_mw
        self._config_tn = config_tn
        if 'pos_filter' not in self._config_tn:
            self._config_tn['pos_filter'] = [['名詞', '一般', '*']]
        self.m = ToolsNLP.MecabWrapper(**self._config_mw)

        print('read data ...')
        self._data = data
        print('{}{:,}'.format('documents count => ',len(self._data)))
        print('tokenize text ...')
        self._texts = self.__tokenizer_text()
        print('make corpus ...')
        self._dictionary, self._corpus, self._texts_cleansing = self.__create_corpus()
        print('{}{:,}'.format('topic count => ',self._num_topics))
        print('make topic model ...')
        self._lda = self.__create_topic_model()
        self._lda_corpus = self._lda[self._corpus]
        print('make output data ...')
        self._topic_list, self._topic_df = self.__count_topic()
        self._df_docweight = self.__proc_docweight()
        print('DONE')

    def __tokenizer_text(self):
        return [self.m.tokenize(sentence=doc[1], is_list=True, **self._config_tn) for doc in self._data]

    def __stop_term(self, is_1len, is_term_fq):
        r = re.compile('^[ぁ-んァ-ン0-9a-zA-Z]$')
        count = Counter(w for doc in self._texts for w in doc)

        if is_1len and is_term_fq:
            return [[w for w in doc if count[w] >= self._stop_term_limitcnt and not re.match(r,w)] for doc in self._texts]
        elif is_1len and not is_term_fq:
            return [[w for w in doc if count[w] >= self._stop_term_limitcnt] for doc in self._texts]
        elif not is_1len and is_term_fq:
            return [[w for w in doc if not re.match(r,w)] for doc in self._texts]
        else:
            return self._texts

    def __create_corpus(self):
        texts = self.__stop_term(self._is_1len, self._is_term_fq)
        dictionary = gensim.corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        return dictionary, corpus, texts
    
    def __create_topic_model(self):
        return gensim.models.ldamodel.LdaModel(corpus=self._corpus
                                                ,id2word=self._dictionary
                                                ,num_topics=self._num_topics
                                                ,iterations=self._iterations
                                                ,alpha=self._alpha
                                                ,dtype=np.float64
                                                )

    def __count_topic(self):
        topic_counnter = Counter(topic[0] for doc in self._lda_corpus for topic in doc if topic[1] > self._topic_doc_threshold).most_common()
        topic_list = list(pd.DataFrame(topic_counnter)[0])
        topic_df = pd.DataFrame(topic_counnter, columns=['topic', 'cnt']).set_index('topic')
        return topic_list, topic_df

    def __proc_docweight(self):
        return pd.DataFrame([{topic[0]:topic[1] for topic in doc if topic[1] > self._topic_doc_threshold} for doc in self._lda_corpus])\
                .join(pd.DataFrame(self._data).rename(columns={0:'url'})['url'], how='inner')

    def get_topic2topdoc_list(self, topic_count=20, top_n=10):
        '''
        Description::
            トピック別のドキュメントのスコア上位のentry_idのデータフレームを出力する
        
        :param topic_count:
            出力するトピック数
            デフォルト：20
        :param top_n:
            出力する記事のスコア上位n
            デフォルト：10

        Usage::
            >>> import ToolsNLP
            # doctest用にエスケースしている。元のコード `data = [i.strip('\n').split('\t') for i in open('data.tsv', 'r')]`
            >>> data = [i.strip('\\n').split('\\t') for i in open('data.tsv', 'r')]
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
            >>> t.get_topic2topdoc_list().head() # モデル作るたびに結果が変わるからエラーになる
                topic                                               url    weight
            103      84  http://news.livedoor.com/article/detail/5022412/  0.973764
            274      84  http://news.livedoor.com/article/detail/5476676/  0.963469
            1149     84  http://news.livedoor.com/article/detail/6468311/  0.955912
            1197     84  http://news.livedoor.com/article/detail/6505621/  0.945417
            1022     84  http://news.livedoor.com/article/detail/6374433/  0.910676
        '''

        df_top_weight = pd.DataFrame()
        for i in self._topic_list[:topic_count]:
            df_top_weight_org = self._df_docweight.sort_values(i, ascending=False).head(top_n).loc[:,['url',i]].rename(columns={i: 'weight'})
            df_top_weight_org['topic'] = i
            df_top_weight = pd.concat([df_top_weight, df_top_weight_org[['topic', 'url', 'weight']]])
        return df_top_weight

    def get_topic2doccnt_plot(self, topic_count=50):
        '''
        Description::
            トピック別の記事数の棒グラフが出力
        
        :param topic_count:
            出力するトピック数
            デフォルト：50

        Usage::
            >>> import ToolsNLP
            # doctest用にエスケースしている。元のコード `data = [i.strip('\n').split('\t') for i in open('data.tsv', 'r')]`
            >>> data = [i.strip('\\n').split('\\t') for i in open('data.tsv', 'r')]
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
            >>> t.get_topic2doccnt_plot()
            >>> 
        '''

        fig = plt.figure(figsize=(20,5))
        plt.subplot(1, 2, 1)
        plt.title('observation cnt')
        (self._topic_df['cnt']).head(topic_count).plot.bar()
        plt.subplot(1, 2, 2)
        plt.title('observation cnt rate')
        (self._topic_df['cnt'] / np.sum(self._topic_df['cnt'])).head(topic_count).plot.bar()
        plt.show()

    def get_topic2term_plot(self, topic_count=20, term_count=200):
        '''
        Description::
            トピック別の単語のワードクラウドが出力
        
        :param topic_count:
            出力するトピック数
            デフォルト：20
        :param term_count:
            トピックに対して紐づくterm数
            デフォルト：200

        Usage::
            >>> import ToolsNLP
            # doctest用にエスケースしている。元のコード `data = [i.strip('\n').split('\t') for i in open('data.tsv', 'r')]`
            >>> data = [i.strip('\\n').split('\\t') for i in open('data.tsv', 'r')]
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
            >>> t.get_topic2term_plot()
            >>> 
        '''
        topic_count = self._num_topics if topic_count >= self._num_topics else topic_count
        loop_count = int(np.ceil(topic_count / 3))
        for i in range(loop_count):
            plt.figure(figsize=(23,loop_count*10))
            for t in range(3*i,3*(i+1)):
                if t+1 <= topic_count:
                    topic = self._topic_list[t]
                    plt.subplot(loop_count,3,t+1)
                    x = dict(self._lda.show_topic(topic,term_count))
                    im = WordCloud(background_color='white',font_path=self._fpath,width=1400,height=700).generate_from_frequencies(x)
                    plt.imshow(im)
                    plt.axis('off')
                    plt.title('Topic #' + str(topic).rjust(3, '0'))
            plt.show()
