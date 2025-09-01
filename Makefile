.PHONY: render-pdf render-pdf-local clean template

TEMPLATE = templates/pandoc/eisvogel.latex
EIS_URL  = https://raw.githubusercontent.com/Wandmalfarbe/pandoc-latex-template/v2.4.0/eisvogel.tex

# Use Debian-based Pandoc image so we can apt-get TeXLive bundles
DOCKER = docker run --rm --platform=linux/amd64 \
	--entrypoint /bin/bash \
	-v "$(PWD)":/work -w /work pandoc/core:3.1

template: $(TEMPLATE)
$(TEMPLATE):
	@mkdir -p templates/pandoc
	curl -fsSL $(EIS_URL) -o $(TEMPLATE)

render-pdf: template
	$(DOCKER) -lc 'apt-get update && \
		DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
			python3 python3-yaml \
			texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended \
			fonts-dejavu && \
		python3 scripts/build_pdf.py'

# Native path (fast on M1/M2) if you install pandoc + BasicTeX locally
render-pdf-local: template
	python3 scripts/build_pdf.py

clean:
	rm -rf out/pdf/*.pdf
