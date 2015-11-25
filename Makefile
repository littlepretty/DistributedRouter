
view: project_report
	open project_report.pdf

project_report: project_report.tex
	pdflatex --enable-write18 project_report.tex
	pdflatex --enable-write18 project_report.tex
