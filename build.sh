#!/bin/sh

# Build the books
asciidoctor -b html -o build/proteomics.html proteomics.adoc
asciidoctor -b html -o build/metabolomics.html metabolomics.adoc

asciidoctor -b html -o build/the-python-lab-book.html complete.adoc

# Build the PDFs
asciidoctor -b pdf -o build/proteomics.pdf proteomics.adoc
asciidoctor -b pdf -o build/metabolomics.pdf metabolomics.adoc

asciidoctor -b pdf -o build/the-python-lab-book.pdf complete.adoc

# Copy the images into location
cp -r ./img ./build/img

cp -r ./covers ./build/img
cp -r ./www ./build
