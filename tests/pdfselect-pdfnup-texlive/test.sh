test a4 20 psselect --pages 1-18
diff psselect-stderr-expected.txt stderr.txt
PYTHONPATH=$TOPDIR python -m psutils.psnup -pa4 -18 < output.pdf > output2.pdf 2> psnup-stderr.txt
diff output2.pdf expected2.pdf
diff psnup-stderr-expected.txt psnup-stderr.txt
