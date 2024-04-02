#!/usr/local/bin/bash
caseformat="^[0-9]{8}"

if [[ $1 =~ $caseformat ]]; then
    cd "/upload/ftp/$1" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        # Rename directories and files with spaces or parentheses
        find . \( -name '* *' -o -name '*(*' -o -name '*)*' \) -exec bash -c '
        for target; do
            dirname=$(dirname "$target")
            base=$(basename "$target")
            # Replace open parentheses with underscore, remove closing parentheses, and replace spaces with underscore
            new_name=$(echo "$base" | tr -d "()" | sed -E "s/\(([0-9])\)/_\1/" | tr " " "_")
            mv "$target" "$dirname/$new_name"
            echo "Renamed: $target -> $dirname/$new_name"
            fixperms "$dirname/$new_name"
        done
        ' bash {} +
    else
        echo "Failed to change directory to /upload/ftp/$1"
    fi
    fixperms ./
else
    echo "Invalid argument format. Argument should match the format $caseformat"
fi
