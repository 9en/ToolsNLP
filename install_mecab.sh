#!/bin/bash

WORK_DIR=`pwd`
echo 'start test' | mecab
is_mecab_install=$?

if [ $is_mecab_install -eq 127 ]; then
    ## mecab
    wget -O mecab-0.996.tar.gz "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7cENtOXlicTFaRUE"
    tar zxvf mecab-0.996.tar.gz
    cd mecab-0.996 && ./configure && make && make install
    cd $WORK_DIR

    ### mecabインストール後にldconfigを実行
    ldconfig

    ## mecab ipadic
    wget -O mecab-ipadic-2.7.0-20070801.tar.gz "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM"
    tar zxvf mecab-ipadic-2.7.0-20070801.tar.gz
    cd mecab-ipadic-2.7.0-20070801 &&./configure --with-charset=utf8 && make && make install

    ## swig install
    sudo apt-get -y install swig-doc swig-examples swig 

    # 動作テスト
    echo 'end test' | mecab
else
    :
fi

rm -rf mecab-*

