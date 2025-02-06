#!/bin/bash

# Save the first call parameter as a variable
filename=$1
basename="${filename%.tex}"

rm -rf build

mkdir -p build
chmod u+w build


pdflatex -output-directory=build -interaction=nonstopmode "$filename"
biber "build/$basename"  # Run biber inside the build directory
pdflatex -output-directory=build -interaction=nonstopmode "$filename"
pdflatex -output-directory=build -interaction=nonstopmode "$filename"

mv "build/$basename.pdf" .