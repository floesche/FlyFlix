.PHONY: localhost update-dependencies install-dependencies show-dependencies

localhost:
	@echo "FlyFlix should be available at http://`ip route get 9.9.9.9 | grep -oP 'src \K[^ ]+'`:17000"
	@python flyflix.py

update-dependencies:
	@pip install --upgrade pip
	@cat requirements.txt | cut -d"=" -f1 | xargs pip install -U

install-dependencies:
	@pip install --upgrade pip
	@pip install -r requirements.txt

show-dependencies:
	@pip freeze | cut -d "=" -f1 | xargs pip show | grep -i "^name\|^version\|^requires"