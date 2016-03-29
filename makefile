
# Linux:
INSTALL_DIR = ~/.config/blender/2.76/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.76/scripts/addons/

SHELL = /bin/sh

SOURCES = ./neuropil_tools/__init__.py ./neuropil_tools/spine_head_analyzer.py ./neuropil_tools/connectivity_tool.py
ZIPFILES = $(SOURCES)

ZIPOPTS = -X -0 -D -o


all: neuropil_tools neuropil_tools.zip


neuropil_tools:
	ln -s . neuropil_tools


neuropil_tools.zip: $(SOURCES)
	@echo Updating neuropil_tools.zip
	@echo Sources = $(SOURCES)
	@zip $(ZIPOPTS) neuropil_tools.zip $(ZIPFILES)


clean:
	rm -f neuropil_tools.zip


install: neuropil_tools.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o neuropil_tools.zip -d $(INSTALL_DIR); \
	fi

