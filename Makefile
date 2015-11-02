all: preprocess build publish

preprocess:
	python ./preprocess.py

build: clean
	asciidoctor -a stylesheet=style.css -a stylesdir=./styles -b html -o build/proteomics.html proteomics.adoc
	asciidoctor -a stylesheet=style.css -a stylesdir=./styles -b html -o build/metabolomics.html metabolomics.adoc
	asciidoctor -a stylesheet=style.css -a stylesdir=./styles -b html -o build/the-python-lab-book.html complete.adoc
	asciidoctor-pdf -o build/proteomics.pdf --trace proteomics.adoc
	asciidoctor-pdf -o build/metabolomics.pdf --trace metabolomics.adoc
	asciidoctor-pdf -o build/the-python-lab-book.pdf complete.adoc
	cp -r ./img/* ./build/img
	cp -r ./covers/* ./build/img
	cp -r ./www/* ./build

publish:
	rsync -zvr ./build/ spenglr@thepythonlabbook.com:/home/spenglr/webapps/thepythonlabbook

clean:
	rm -r ./build
 
