test a4 20 pdfselect --pages 1-18
diff pdfselect-stderr-expected.txt stderr.txt
pdfnup -pa4 -18 < output.pdf > output2.pdf 2> pdfnup-stderr.txt
diff output2.pdf expected2.pdf
diff pdfnup-stderr-expected.txt pdfnup-stderr.txt
