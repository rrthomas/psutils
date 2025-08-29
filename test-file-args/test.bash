#!/bin/bash

mkdir -p results
rm -f results/*

success() {
	printf "\n\033[92mSUCCESS\x1b[0m\n\n"
}
failure() {
	printf "\n\033[91mFAILURE\x1b[0m\n\n"
}

echo
echo '###############'
echo '### epsffit ###'
echo '###############'
echo

epsffit_want=$(md5sum outputs/epsffit.eps | cut -d' ' -f1)

# fin stdout
out=results/epsffit_fin_stdout.eps
epsffit 20mm 20mm 120mm 120mm inputs/sample-1.eps > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/epsffit_fin_dashout.eps
epsffit 20mm 20mm 120mm 120mm inputs/sample-1.eps - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

# stdin stdout
out=results/epsffit_stdin_stdout.eps
< inputs/sample-1.eps epsffit 20mm 20mm 120mm 120mm > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/epsffit_dashin_fout.eps
< inputs/sample-1.eps epsffit 20mm 20mm 120mm 120mm - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/epsffit_dashin_stdout.eps
< inputs/sample-1.eps epsffit 20mm 20mm 120mm 120mm - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/epsffit_dashin_dashout.eps
< inputs/sample-1.eps epsffit 20mm 20mm 120mm 120mm - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$epsffit_want" ]]; then success; else failure; fi

echo
echo '##################'
echo '### extractres ###'
echo '##################'
echo

extractres_want=$(md5sum outputs/extractres.eps | cut -d' ' -f1)

# fin stdout
out=results/extractres_fin_stdout.eps
extractres inputs/sample-1.eps > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/extractres_fin_dashout.eps
extractres inputs/sample-1.eps - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

# stdin stdout
out=results/extractres_stdin_stdout.eps
< inputs/sample-1.eps extractres > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/extractres_dashin_fout.eps
< inputs/sample-1.eps extractres - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/extractres_dashin_stdout.eps
< inputs/sample-1.eps extractres - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/extractres_dashin_dashout.eps
< inputs/sample-1.eps extractres - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$extractres_want" ]]; then success; else failure; fi

### includeres ###

echo
echo '##################'
echo '### includeres ###'
echo '##################'
echo

includeres_want=$(md5sum outputs/includeres.eps | cut -d' ' -f1)

# fin stdout
out=results/includeres_fin_stdout.eps
includeres inputs/sample-1.eps > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/includeres_fin_dashout.eps
includeres inputs/sample-1.eps - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

# stdin stdout
out=results/includeres_stdin_stdout.eps
< inputs/sample-1.eps includeres > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/includeres_dashin_fout.eps
< inputs/sample-1.eps includeres - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/includeres_dashin_stdout.eps
< inputs/sample-1.eps includeres - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/includeres_dashin_dashout.eps
< inputs/sample-1.eps includeres - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$includeres_want" ]]; then success; else failure; fi

echo
echo '##############'
echo '### psbook ###'
echo '##############'
echo

psbook_want=$(md5sum outputs/psbook.pdf | cut -d' ' -f1)

# fin stdout
out=results/psbook_fin_stdout.pdf
psbook inputs/input_1.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/psbook_fin_dashout.pdf
psbook inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

# stdin stdout
out=results/psbook_stdin_stdout.pdf
< inputs/input_1.pdf psbook > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/psbook_dashin_fout.pdf
< inputs/input_1.pdf psbook - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/psbook_dashin_stdout.pdf
< inputs/input_1.pdf psbook - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/psbook_dashin_dashout.pdf
< inputs/input_1.pdf psbook - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psbook_want" ]]; then success; else failure; fi

echo
echo '##############'
echo '### psjoin ###'
echo '##############'
echo

psjoin_want=$(md5sum outputs/psjoin.pdf | cut -d' ' -f1)
psjoin_want_2=$(md5sum outputs/psjoin2.pdf | cut -d' ' -f1)

# f1 f2
out=results/psjoin_f1_f2.pdf
psjoin inputs/input_1.pdf inputs/input_2.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psjoin_want" ]]; then success; else failure; fi

# dash f
rm -f -- -
out=results/psjoin_dash_f.pdf
< inputs/input_1.pdf psjoin - inputs/input_2.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psjoin_want" ]]; then success; else failure; fi

# f dash
rm -f -- -
out=results/psjoin_f_dash.pdf
< inputs/input_2.pdf psjoin inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psjoin_want" ]]; then success; else failure; fi

echo
echo '#############'
echo '### psnup ###'
echo '#############'
echo

psnup_want=$(md5sum outputs/psnup.pdf | cut -d' ' -f1)

# fin stdout
out=results/psnup_fin_stdout.pdf
psnup -2 inputs/input_1.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/psnup_fin_dashout.pdf
psnup -2 inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

# stdin stdout
out=results/psnup_stdin_stdout.pdf
< inputs/input_1.pdf psnup -2 > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/psnup_dashin_fout.pdf
< inputs/input_1.pdf psnup -2 - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/psnup_dashin_stdout.pdf
< inputs/input_1.pdf psnup -2 - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/psnup_dashin_dashout.pdf
< inputs/input_1.pdf psnup -2 - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psnup_want" ]]; then success; else failure; fi

echo
echo '################'
echo '### psresize ###'
echo '################'
echo

psresize_want=$(md5sum outputs/psresize.pdf | cut -d' ' -f1)

# fin stdout
out=results/psresize_fin_stdout.pdf
psresize -p a4 inputs/input_1.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/psresize_fin_dashout.pdf
psresize -p a4 inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

# stdin stdout
out=results/psresize_stdin_stdout.pdf
< inputs/input_1.pdf psresize -p a4 > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/psresize_dashin_fout.pdf
< inputs/input_1.pdf psresize -p a4 - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/psresize_dashin_stdout.pdf
< inputs/input_1.pdf psresize -p a4 - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/psresize_dashin_dashout.pdf
< inputs/input_1.pdf psresize -p a4 - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psresize_want" ]]; then success; else failure; fi

echo
echo '################'
echo '### psselect ###'
echo '################'
echo

psselect_want=$(md5sum outputs/psselect.pdf | cut -d' ' -f1)

# fin stdout
out=results/psselect_fin_stdout.pdf
psselect 1 inputs/input_1.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/psselect_fin_dashout.pdf
psselect 1 inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

# stdin stdout
out=results/psselect_stdin_stdout.pdf
< inputs/input_1.pdf psselect 1 > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/psselect_dashin_fout.pdf
< inputs/input_1.pdf psselect 1 - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/psselect_dashin_stdout.pdf
< inputs/input_1.pdf psselect 1 - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/psselect_dashin_dashout.pdf
< inputs/input_1.pdf psselect 1 - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$psselect_want" ]]; then success; else failure; fi

echo
echo '##############'
echo '### pstops ###'
echo '##############'
echo

pstops_want=$(md5sum outputs/pstops.pdf | cut -d' ' -f1)

# fin stdout
out=results/pstops_fin_stdout.pdf
pstops -r inputs/input_1.pdf > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi

# fin dashout
rm -f -- -
out=results/pstops_fin_dashout.pdf
pstops -r inputs/input_1.pdf - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi

# stdin stdout
out=results/pstops_stdin_stdout.pdf
< inputs/input_1.pdf pstops -r > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi

# dashin fout
rm -f -- -
out=results/pstops_dashin_fout.pdf
< inputs/input_1.pdf pstops -r - "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi

# dashin stdout
rm -f -- -
out=results/pstops_dashin_stdout.pdf
< inputs/input_1.pdf pstops -r - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi

# dashin dashout
rm -f -- -
out=results/pstops_dashin_dashout.pdf
< inputs/input_1.pdf pstops -r - - > "$out"
has=$(md5sum "$out" | cut -d' ' -f1)
if [[ "$has" == "$pstops_want" ]]; then success; else failure; fi
