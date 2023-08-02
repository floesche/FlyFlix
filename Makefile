.PHONY: localhost reinstall-venv update-dependencies install-dependencies show-dependencies

localhost:
	@python flyflix.py

reinstall-venv:
	@rm -rf .venv
	@python -m venv .venv

update-dependencies:
	@pip install --upgrade pip
	@cat requirements.txt | cut -d"=" -f1 | xargs pip install -U

install-dependencies:
	@pip install --upgrade pip
	@pip install -r requirements.txt

show-dependencies:
	@pip freeze | cut -d "=" -f1 | xargs pip show | grep -i "^name\|^version\|^requires"