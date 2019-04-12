#! -*- coding: utf-8 -*-

import os
import MeCab
import neologdn
import subprocess
import json
import re
from pathlib import Path
import site


class Tokenizer:
    def __add_pos(self, is_pos, term, pos):
        if term:
            if is_pos:
                return term + ':' + '-'.join(pos)
            else:
                return term

    def _stopword_list(self, stopword):
        stopword_list = []
        if stopword:
            stopword_list = [(i.strip('\n')).lower() for i in open(stopword, 'r', encoding='utf-8') if i.strip('\n')]
        return stopword_list

    def __pos_filter(self, sentence_parsed_term, pos_filter, is_org, is_pos, stopword_list):
        term = sentence_parsed_term.split('\t')[0]
        term_pos = sentence_parsed_term.split('\t')[1].split(',')
        pos_filter_result = ''
        # filter: on or off
        if pos_filter != [[]]:
            # loop pos list
            for pos in pos_filter:
                # pos extract
                if pos == term_pos[:3]:
                    pos_filter_result = self._term_to_base(term=term.replace(' ', '-'), term_base=term_pos[6].replace(' ', '-'), is_org=is_org)
        else:
            pos_filter_result = self._term_to_base(term=term.replace(' ', '-'), term_base=term_pos[6].replace(' ', '-'), is_org=is_org)
        # stop word
        term_result = None if pos_filter_result.lower() in stopword_list else pos_filter_result
        # add pos
        return self.__add_pos(is_pos, term_result, term_pos[:3])

    def _proc_normalized(self, sentence, is_normalized):
        if is_normalized:
            return self._mecabObj.parse(neologdn.normalize(sentence))
        else:
            return self._mecabObj.parse(sentence)

    def _proc_term(self, sentence_parsed, pos_filter, is_org, is_pos):
        pos_result = []
        # loop term parse pos
        for sentence_parsed_term in sentence_parsed.split('\n'):
            # escape EOS
            if sentence_parsed_term not in ['EOS', '']:
                filter_result = self.__pos_filter(sentence_parsed_term, pos_filter ,is_org ,is_pos ,self.stopword_list)
                # append not None result
                if filter_result:
                    pos_result.append(filter_result)
        return pos_result

class TokenizerSentiment:
    def _split_sentence(self, text):
        for sentence in self.re_delimiter.split(neologdn.normalize(text)):
            if sentence and not self.re_delimiter.match(sentence):
                yield sentence

    def __lookup_wago(self, lemma, lemmas, lemmas_negation):
        if lemma in self.wago_dict:
            polarity = 1 if self.wago_dict[lemma].startswith('ポジ') else -1
            return polarity, lemma
        for i in range(5, 0, -1):
            wago = ' '.join(lemmas[-i:]) + ' ' + lemma
            if wago in self.wago_dict:
                polarity = 1 if self.wago_dict[wago].startswith('ポジ') else -1
                if len(lemmas_negation) > 0:
                    if lemmas_negation[-1] in wago:
                        return None, wago
                    else:
                        return polarity, wago
        return None, lemma

    def _proc_sentiment(self, sentence, is_term):
        sentence_parsed = self._mecabObj.parse(neologdn.normalize(sentence))
        polarities = []
        lemmas = []
        lemmas_negation = []
        # loop term parse pos
        for sentence_parsed_term in sentence_parsed.split('\n'):
            # escape EOS
            if sentence_parsed_term not in ['EOS', '']:
                polarity, lemma, polarities, lemmas, lemmas_negation = self.__calc_sentiment_polarity(sentence_parsed_term ,is_term, lemmas, polarities, lemmas_negation)
                # append not None result
                if polarity:
                    polarities.append([lemma,polarity])
                    lemmas_negation.append(lemma)
        if not polarities and is_term:
            return None
        elif not polarities and not is_term:
            return None
        
        score = sum([i[1] for i in polarities]) / len(polarities)
        if is_term:
            return {'score':score, 'cnt':len(polarities),'polarities':polarities}
        else:
            return score

    def __calc_sentiment_polarity(self, sentence, is_term, lemmas, polarities, lemmas_negation):
        term = sentence.split('\t')[0]
        term_pos = sentence.split('\t')[1].split(',')
        lemma = self._term_to_base(term=term.replace(' ', '-'), term_base=term_pos[6].replace(' ', '-'), is_org=True)
        if lemma in self.noun_dict:
            polarity = 1 if self.noun_dict[lemma] == 'p' else -1
        else:
            polarity, lemma = self.__lookup_wago(lemma, lemmas, lemmas_negation)
            if not polarity and len(polarities) > 0 and lemma in self.negation and lemmas_negation[-1] in lemmas[-3:]:
                polarities[-1][1] *= -1
                polarities[-1][0] = lemmas_negation[-1] + '-' + lemma
        # stop word
        if not lemma.lower() in self.stopword_list:
            lemmas.append(lemma)
        return polarity, lemma, polarities, lemmas, lemmas_negation

    def _make_noun_dict(self, fname):
        sitedir = site.getsitepackages()[-1]
        installdir = os.path.join(sitedir, 'ToolsNLP')
        dict_path = installdir + "/sentiment_dict/pn_noun.json"
        default_dict = json.load(open(dict_path, 'r'))
        if fname:
            with open(fname, 'r') as fd:
                word_dict = {}
                for line in fd:
                    word, polarity = line.strip().split(',')
                    if polarity == 'e' or polarity == 'ニュートラル':
                        try:
                            default_dict.pop(word)
                        except:
                            continue
                    else:
                        word_dict[word] = polarity
            return {**default_dict, **word_dict}
        else:
            return default_dict

    def _make_wago_dict(self, fname):
        sitedir = site.getsitepackages()[-1]
        installdir = os.path.join(sitedir, 'ToolsNLP')
        dict_path = installdir + "/sentiment_dict/pn_wago.json"
        default_dict = json.load(open(dict_path, 'r'))
        if fname:
            with open(fname, 'r') as fd:
                word_dict = {}
                for line in fd:
                    word, polarity = line.strip().split(',')
                    if polarity == 'e' or polarity == 'ニュートラル':
                        try:
                            default_dict.pop(word)
                        except:
                            continue
                    else:
                        word_dict[word] = polarity
            return {**default_dict, **word_dict}
        else:
            return default_dict


class MecabWrapper(Tokenizer, TokenizerSentiment):
    '''
    Description::
        Mecabのインスタンスを生成する
    
    :param dicttype:
        参照する辞書のタイプを指定
        ipadic(defalt) or neologd
    :param userdict:
        形態素解析用のユーザ辞書ファイルのファイル名を指定
        サンプルファイル
            オオカミくんには騙されない,0,0,0,名詞,固有名詞,一般,*,*,*,オオカミくんには騙されない,オオカミクンニハダマサレナイ,オオカミクンニハダマサレナイ
            ※最終行に改行があるとエラーになる
    :param stopword:
        ストップワードのファイル名を指定
        1行1単語で改行してファイルを作成する
        例:
        $cat stopword.txt
        3人
        さん
    :param noundict:
        センチメント分析用の名詞辞書ファイルのファイル名を指定
        サンプルファイル(p:ポジティブ,n:ネガティブ,e:ニュートラル)
            醵金,p
            隘路,n
    :param wagodict:
        センチメント分析用の用言辞書ファイルのファイル名を指定
        サンプルファイル(ポジ:ポジティブ,ネガ:ネガティブ)
            あがく,ネガ
            颯爽 の,ポジ
    :param negation:
        センチメント分析用の打消し語の指定
        例：['ず','ない']
        デフォルト：['ない', 'ず', 'ぬ']

    Usage::
        >>> import ToolsNLP
        >>> text = '稲垣吾郎さん、草彅剛さん、香取慎吾さんの3人によるレギュラー番組 『7.2 新しい別の窓』や『オオカミくんには騙されない』'
        >>>
        >>> m = ToolsNLP.MecabWrapper()
        >>> m.tokenize(sentence=text)
        '稲垣 吾郎 さん 、 草 彅剛 さん 、 香取 慎吾 さん の 3 人 による レギュラー 番組 『 7 . 2 新しい 別 の 窓 』 や 『 オオカミ くん に は 騙す れる ない 』'
        >>>
        >>> m = ToolsNLP.MecabWrapper(dicttype='neologd')
        >>> m.tokenize(sentence=text)
        '稲垣吾郎 さん 、 草彅剛 さん 、 香取慎吾 さん の 3人 による レギュラー番組 『 7 . 2 新しい別の窓 』 や 『 オオカミ くん に は 騙す れる ない 』'
        >>>
        >>> m = ToolsNLP.MecabWrapper(dicttype='neologd', userdict='userdict.csv')
        >>> m.tokenize(sentence=text)
        '稲垣吾郎 さん 、 草彅剛 さん 、 香取慎吾 さん の 3人 による レギュラー番組 『 7 . 2 新しい別の窓 』 や 『 オオカミくんには騙されない 』'
        >>>
        >>> m = ToolsNLP.MecabWrapper(dicttype='neologd', userdict='userdict.csv', stopword='stopword.txt')
        >>> m.tokenize(sentence=text)
        '稲垣吾郎 、 草彅剛 、 香取慎吾 の による レギュラー番組 『 7 . 2 新しい別の窓 』 や 『 オオカミくんには騙されない 』'
    '''
    def __init__(self, dicttype='ipadic', userdict='', stopword='', noundict='', wagodict='', negation=[]):
        self._dicttype = dicttype
        self._userdict = userdict
        self._userdict_name = self._userdict.replace("csv", "dict").split('/')[-1]
        self._path_mecab_config = self.__shell_check_output('which mecab-config')
        self._path_mecab_dict = self.__get_mecab_path('dicdir')
        self._path_mecab_libexe = self.__get_mecab_path('libexecdir')
        self.stopword_list = self._stopword_list(stopword)
        self.noun_dict = self._make_noun_dict(noundict)
        self.wago_dict = self._make_wago_dict(wagodict)
        self.re_delimiter = re.compile("[。,．!\?|(笑 )]")
        self.negation = ['ない', 'ず', 'ぬ'] + negation
        self._mecabObj = self.__CallMecab()

    def __shell_check_output(self, str_cmd):
        return subprocess.check_output(str_cmd, shell=True).decode('utf-8').strip('\n')

    def __get_mecab_path(self, get_type):
        str_cmd = "echo `{0} --{1}`".format(self._path_mecab_config, get_type)
        return self.__shell_check_output(str_cmd)

    def __CompileUserdict(self):
        cmCompileDict = u'{0}/mecab-dict-index -d {1}/ipadic -u {2} -f utf-8 -t utf-8 {3} > /dev/null'.\
                format(self._path_mecab_libexe, self._path_mecab_dict, self._userdict_name, self._userdict)
        try:
            subprocess.call(cmCompileDict, shell=True)
        except OSError as e:
            sys.exit('Failed to compile mecab userdict. System ends')

    def __CallMecab(self):
        cmMecabInitialize = ''
        if self._userdict:
            self.__CompileUserdict()
            cmMecabInitialize += '-u {} '.format(self._userdict_name)
        if self._dicttype == 'neologd':
            cmMecabInitialize += '-d {} '.format(os.path.join(self._path_mecab_dict, "mecab-ipadic-neologd"))
        try:
            mecabObj = MeCab.Tagger(cmMecabInitialize)
        except Exception as e:
            raise subprocess.CalledProcessError(returncode=-1, cmd="Failed to initialize Mecab object")
        return mecabObj

    def _term_to_base(self, term, term_base, is_org):
        if is_org:
            return term if term_base == '*' else term_base
        else:
            return term

    def tokenize(self, sentence, pos_filter=[[]], is_normalized=True, is_org=True, is_pos=False, is_list=False):
        '''
        Description::
            テキストをtermに分割する

        :param sentence:
            入力テキスト
        :param pos_filter:
            品詞フィルタ（3階層まで指定する）。複数ある場合は配列で追加する。
            [['名詞', '一般', '*']]
            参考URL：http://www.unixuser.org/~euske/doc/postag/
            ※IPA品詞体系
        :param is_normalized:
            入力テキストを正規化するかどうか
            neologd推奨の方法にて正規化：https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
            デフォルトがTrue（正規化する）
        :param is_org:
            形態素解析後、標準系（原形）に変換するかどうか
            名詞でもカタカナ英語を英語に変換してくれたりするので名詞だけでもTrueにするのを推奨
            デフォルトがTrue（標準系に変換する）
        :param is_pos:
            出力結果に品詞体系を追加するかどうか
            デフォルトがFalse（品詞体系を追加しない）
        :param is_list:
            出力結果を配列にするか文字列にするかどうか
            デフォルトがFalse（文字列出力）

        Usage::
        >>> import ToolsNLP
        >>> text = '稲垣吾郎さん、草彅剛さん、香取慎吾さんの3人によるレギュラー番組 『7.2 新しい別の窓』や『オオカミくんには騙されない』'
        >>> m = ToolsNLP.MecabWrapper(dicttype='neologd', userdict='userdict.csv', stopword='stopword.txt')
        >>> m.tokenize(sentence=text)
        '稲垣吾郎 、 草彅剛 、 香取慎吾 の による レギュラー番組 『 7 . 2 新しい別の窓 』 や 『 オオカミくんには騙されない 』'
        >>>
        >>> m.tokenize(sentence=text, pos_filter=[['名詞', '固有名詞', '一般']])
        '草彅剛 レギュラー番組 新しい別の窓 オオカミくんには騙されない'
        >>>
        >>> m.tokenize(sentence=text, pos_filter=[['名詞', '固有名詞', '一般']], is_pos=True)
        '草彅剛:名詞-固有名詞-一般 レギュラー番組:名詞-固有名詞-一般 新しい別の窓:名詞-固有名詞-一般 オオカミくんには騙されない:名詞-固有名詞-一般'
        >>>
        >>> m.tokenize(sentence=text, pos_filter=[['名詞', '固有名詞', '一般']], is_list=True)
        ['草彅剛', 'レギュラー番組', '新しい別の窓', 'オオカミくんには騙されない']
        >>>
        '''
        sentence_parsed = self._proc_normalized(sentence, is_normalized)
        pos_result = self._proc_term(sentence_parsed, pos_filter ,is_org ,is_pos)
        return pos_result if is_list else ' '.join(map(str, filter(None, pos_result))).strip() # output: str or list


    def tokenize_sentiment(self, text, is_term=False):
        '''
        Description::
            テキストをtermに分割する

        :param text:
            入力テキスト
        :param is_term:
            ポジネガ単語別の評価値を表示するかどうか
            デフォルトがFalse（ポジネガ単語を表示しないで集計結果のみ）

        Usage::
        >>> import ToolsNLP
        >>> text = 'この2人のやりとりはやっぱり面白い！観てて飽きない！'
        >>> m = ToolsNLP.MecabWrapper(dicttype='neologd')
        >>> m.tokenize_sentiment(text=text)
        [1.0, 1.0]
        >>>
        >>> m.tokenize_sentiment(text=text, is_term=True)
        [{'score': 1.0, 'cnt': 1, 'polarities': [['面白い', 1]]}, {'score': 1.0, 'cnt': 1, 'polarities': [['飽きる-ない', 1]]}]
        >>>
        '''
        scores = []
        for sentence in self._split_sentence(text):
            score = self._proc_sentiment(sentence, is_term)
            if score:
                scores.append(score)
        return scores

