#!/usr/bin/env bash

if [ "${NEXT_ACTION}" == "deploy" ]; then
    # Use no input to skip the verification step in collectstatic.
    deploy_command="python manage.py collectstatic --noinput && python manage.py set_app_hash"

    if [ "${MIGRATION_NEEDED}" == "true" ]; then
        deploy_command="${deploy_command} && yes "yes" | python manage.py migrate"
    fi

    if [ "${INDEXING_NEEDED}" == "true" ] ; then
        deploy_command="${deploy_command} && python manage.py index -f"

        # Put every mention of an index file change into an array.
        changed_files=()
        while read -r line; do
            changed_files+=("$line")
        done <<< "$(git log ${TRAVIS_COMMIT_RANGE} --name-only --pretty=format: '**/search.py' | awk NF)"

        # Filter out the duplicate file names, since we only want to run once per type.
        changed_files_uniq=($(printf "%s\n" "${changed_files[@]}" | sort | uniq -c | awk '{ print $2 }'))

        # Create the actual targets string.
        targets=""
        for filename in ${changed_files_uniq[@]}; do
            targets="${targets},$(dirname "${filename}" | tr / .)"
        done

        # Append the targets to the index command, strip the first comma.
        deploy_command="${deploy_command} -t ${targets:1}"
    fi

    if [ "${MIGRATION_NEEDED}" == "true" ] || [ "${INDEXING_NEEDED}" == "true" ] ; then
        # Scale the beat dynos up after a successful deployment.
        deploy_command="${deploy_command} && python ./ci/patch_heroku_app.py '${HEROKU_APP_NAME}/formation/beat' '${HEROKU_API_KEY}' 'quantity' '1'"

        # Set the heroku maintenance mode off after the deploy.
        deploy_command="${deploy_command} && python ./ci/patch_heroku_app.py '${HEROKU_APP_NAME}' '${HEROKU_API_KEY}' 'maintenance' 'false'"
    fi

    echo "${deploy_command}"
fi
