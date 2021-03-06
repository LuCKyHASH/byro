#!/bin/bash

if [ "$1" == '--help' ]; then
  echo "Install all plugins from the 'local' directory."
  exit 0
fi

for plugin in local/*; do
  echo installing $plugin

  cd $plugin
  python setup.py develop
  cd -
done
