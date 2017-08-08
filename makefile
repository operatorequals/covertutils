
PY=$(which python)
PY='python'

clean :
	# find ./covertutils/ tests/ examples/ -name "*.pyc" -exec rm {} \;
	find . -name "*.pyc" -exec rm {} \;
	rm -r docs/_build/ __pycache__

test :
	clear;$(PY) -m unittest  discover -v  ./tests

doc :
	# cd docs/;
	sphinx-apidoc ./covertutils/ -P -f  -o docs/
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
	PYTHONPATH=".:${PYTHONPATH}" ${EX}


compile :
	cython ${PY} --embed -o cythoned.c
	gcc cythoned.c -lpython2.7  -I "/usr/include/python2.7" -o ${EX} -ldl
	rm cythoned.c


elf :
# --exclude-module 'Tkinter, numpy, curses, tcl, pywin'
	pyinstaller --onefile --noconsole --hidden-import 'covertutils'  -n ${EX} ${PY}
	mv dist/${EX} .
	rm -r build/
	rm ${EX}.spec

exe :
# , covertutils.payloads.linux.shellcode'
	wine ~/.wine/drive_c/Python27/Scripts/pyinstaller.exe\
	 --onefile --noconsole\
	 --hidden-import 'covertutils'\
	 --hidden-import 'covertutils.payloads'\
	 --hidden-import 'covertutils.payloads.linux'\
	 --hidden-import 'covertutils.payloads.linux.shellcode'\
	 --exclude-module 'Tkinter, numpy, curses, tcl, pywin, urllib, urllib2, xml, unittest, _gtkagg, _tkagg'  -n ${EX} ${PY}
	mv dist/${EX} .
	rm -r build/
	rm ${EX}.spec


publish :
	python setup.py sdist build
	twine upload dist/*



nui_elf :
	nuitka --standalone --remove-output ${PY}
	# wine /home/unused/.wine/drive_c/Python27/python.exe /home/unused/.wine/drive_c/Python27/Scripts/nuitka --standalone --remove-output ${PY}


pack :
	-rm -r target
	-rm target.pyz
	mkdir target
	cp -r covertutils target/
	cat ${PY} >> target/covertutils/__init__.py
	# cat ${PY} >> target/covertutils/main.py
	# zip -r -9 target.pyz target
	cd target && zip -r -9 -q target.pyz covertutils
	mv target/target.pyz .
	# cd ..
	# cp ${PY} main.py
	# touch __init__.py
	# zip -9 -u target.pyz main.py __init__.py
	# rm -r target
