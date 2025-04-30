genexecutable:
	cp main.py unitapi
	sed  -i '1i #!/usr/bin/python\n' unitapi

install: genexecutable
	sudo cp unitapi /usr/bin/
	sudo chmod +x /usr/bin/unitapi
	rm unitapi