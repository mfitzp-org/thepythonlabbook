#!/bin/sh

# Build the books
asciidoctor -b html -o build/proteomics.html book-proteomics.adoc
asciidoctor -b html -o build/metabolomics.html book-metabolomics.adoc

# Build the PDFs
asciidoctor -b pdf -o build/proteomics.pdf book-proteomics.adoc
asciidoctor -b pdf -o build/metabolomics.pdf book-metabolomics.adoc

# Copy the images into location
cp -r ./img ./build/img