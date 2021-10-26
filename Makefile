localhost:
	@echo "FlyFlix should be available at port :17000"
	@python flyflix.py

update:
	@pip install --upgrade pip
	@pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U