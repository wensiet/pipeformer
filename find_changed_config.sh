#!/bin/bash

file_list=$(git diff-tree --no-commit-id --name-status -r $CI_COMMIT_SHA)

filename=""

words=($file_list)

if [ "${#words[@]}" -ne 2 ]; then
  echo Detected more than one change
  return 1
fi


change_type="${words[0]}"
file_name="${words[1]}"

case $change_type in
      "A") echo "Added: $file_name" ;;
      "D") echo "Deleted: $file_name" ;;
      "M") echo "Modified: $file_name" ;;
      "R") echo "Renamed: $file_name" ;;
esac

export file_name=$file_name
export change_type=$change_type
