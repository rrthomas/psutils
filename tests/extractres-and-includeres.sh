# includeres test uses the resources extracted by extractres
test a4 1 extractres
$srcdir/psutils-wrapper includeres $srcdir/extractres-and-includeres-expected.ps > tests/includeres-output.ps
diff tests/includeres-output.ps $srcdir/includeres-expected.ps && \
    diff ISO-8859-1Encoding.enc $srcdir/ISO-8859-1Encoding-expected.enc && \
    diff a2ps-a2ps-hdr2.02.ps $srcdir/a2ps-a2ps-hdr2.02-expected.ps && \
    diff a2ps-black+white-Prolog2.01.ps $srcdir/a2ps-black+white-Prolog2.01-expected.ps
