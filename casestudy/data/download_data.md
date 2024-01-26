# Download all files from csv.

**Windows**
`gc .\file.csv |%{iwr $_-outf $(split-path $_-leaf)}`

**Linux**
`wget -i file.csv`