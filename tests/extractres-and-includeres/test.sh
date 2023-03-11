# includeres test uses the resources extracted by extractres
test a4 1 extractres
includeres expected.ps > includeres-output.ps
diff includeres-output.ps includeres-expected.ps && \
    diff ISO-8859-1Encoding.enc ISO-8859-1Encoding-expected.enc && \
    diff a2ps-a2ps-hdr2.02.ps a2ps-a2ps-hdr2.02-expected.ps && \
    diff a2ps-black+white-Prolog2.01.ps a2ps-black+white-Prolog2.01-expected.ps
