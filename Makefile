all:
	rm -rf ./dist
	mkdir dist
	cp -r ./src/* ./dist/
	cp -r ./lib/python2.7/site-packages/* ./dist/
	chmod -R 777 dist
	cd dist && zip lambda ./*

clean:
	rm -rf ./dist
