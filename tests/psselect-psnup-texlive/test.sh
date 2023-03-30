test a4 20 psselect --pages 1-18
diff psselect-stderr-expected.txt stderr.txt
psnup -pa4 -18 < output.ps > output2.ps 2> psnup-stderr.txt
diff output2.ps expected2.ps
diff psnup-stderr-expected.txt psnup-stderr.txt
