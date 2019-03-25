test:
	@cd tests && python3 test_ToolsNLP.py

install_mecab:
	sudo bash install_mecab.sh

install_neologd:
	wget --no-check-certificate https://github.com/neologd/mecab-ipadic-neologd/tarball/master -O mecab-ipadic-neologd.tar
	tar -xvf mecab-ipadic-neologd.tar
	sudo mv neologd-mecab-ipadic-neologd-* neologd-mecab-ipadic-neologd && cd neologd-mecab-ipadic-neologd && ( echo yes | ./bin/install-mecab-ipadic-neologd )
	sudo rm -rf mecab* && rm -rf neologd*
