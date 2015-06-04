#!/bin/bash

git fetch --tags

# set the output pre and postfix
if [[ "$@" == *"--verbose"* ]]
then
    cmd_prefix="    heroku run python manage.py"
else
    cmd_prefix="heroku run python manage.py"
fi

if [[ "$@" == *"--staging"* ]]
then
    cmd_postfix="-a hellolily-staging"
else
    cmd_postfix="-a hellolily"
fi


# get just the tag, strip the number of commits ahead and short commit hash
current_tag_full=$(git describe --tag)
current_tag=$(cut -d '-' -f1 <<< "$current_tag_full")

current_branch="$(git symbolic-ref --short -q HEAD)"
compare_to="origin/$current_branch"

# diff between the last tag and current branch and look for certain changes
diff="git diff --name-only --diff-filter=ACMRTUXB $current_tag...$compare_to"

migration_grep="$diff | grep /migrations/"
if [ "$(eval $migration_grep -c)" != "0" ]
then
    if [[ "$@" == *"--verbose"* ]]
    then
        for file in $(eval $migration_grep)
        do
            author=""
            if [[ "$@" == *"--author"* ]]
            then
                author=" ($(git log --format="%an" -n 1 $compare_to -- $file))"
            fi
            filename=$(cut -d '/' -f1 <<< $(echo "$file" | rev) | rev)
            label=$(cut -d '/' -f3 <<< $(echo "$file" | rev) | rev)
            echo "$label ${filename:0:4}$author"
        done
        echo ""
    fi
    echo "$cmd_prefix migrate $cmd_postfix"
else
    if [[ "$@" == *"--verbose"* ]]
    then
        echo ""
        echo "no new migrations"
    fi
fi

static_grep="$diff | grep -E '\.(css|eot|flv|gif|ico|jpg|jpeg|js|otf|png|svg|swf|ttf|woff|woff2)$'"
if [ "$(eval $static_grep -c)" != "0" ]
then
    if [[ "$@" == *"--verbose"* ]]
    then
        echo ""
        for file in $(eval $static_grep)
        do
            author=""
            if [[ "$@" == *"--author"* ]]
            then
                author=" ($(git log --format="%an" -n 1 $compare_to -- $file))"
            fi
            echo "$file$author"
        done
        echo ""
    fi
    echo "$cmd_prefix collectstatic --noinput $cmd_postfix"
else
    if [[ "$@" == *"--verbose"* ]]
    then
        echo ""
        echo "no new static files"
    fi
fi

search_grep="$diff | grep search.py$"
if [ "$(eval $search_grep -c)" != "0" ]
then
    if [[ "$@" == *"--verbose"* ]]
    then
        echo ""
        for file in $(eval $search_grep)
        do
            author=""
            if [[ "$@" == *"--author"* ]]
            then
                author=" ($(git log --format="%an" -n 1 $compare_to -- $file))"
            fi
            echo "$file$author"
        done
        echo ""
    fi
    echo "$cmd_prefix index $cmd_postfix"
else
    if [[ "$@" == *"--verbose"* ]]
    then
        echo ""
        echo "no new search mappings"
    fi
fi
