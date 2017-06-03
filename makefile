
PY=$(which python)
PY='python'

clean :
	find ./covertutils/ tests/ -name "*.pyc" -exec rm {} \;

test :
	clear;$(PY) -m unittest  discover -v  ./tests


docs :
	mkdir docs


doc : docs
	cd docs/;
	sphinx-apidoc ./covertutils/ -P -f -o docs/
	cd docs/;make html


see_doc : doc
	firefox $(PWD)/docs/_build/html/index.html &


gh-pages : doc
	rm -rf gh-pages/*
	cp  -rf docs/_build/html/* gh-pages/
	git checkout gh-pages

	git add gh-pages/
	git commit -m "Docs Update" gh-pages
	git push -f gh-pages

	git checkout master


coverage :
	-coverage run --source=covertutils/ -m unittest discover -s tests/
	coverage html
	firefox htmlcov/index.html


cov-badge :
	-coverage run --source=covertutils/ -m unittest discover -s tests/
	coverage-badge -o cov-badge.svg


run :
	PYTHONPATH=".:PYTHONPATH" ${EX}


compile :
	cython ${SRC} --embed -o cythoned.c
	gcc cythoned.c -lpython2.7  -I "/usr/include/python2.7" -o ${EX} -ldl
	rm cythoned.c


elf :
	pyinstaller --onefile --noconsole --hidden-import 'covertutils' -n ${EX} ${PY}
	mv dist/${EX} .
	rm -r build/
	rm ${EX}.spec
