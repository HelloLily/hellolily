import requests
import sys


def send_patch_request_to_heroku_app(app_name, api_key, data_key, data_value):
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': 'Bearer {0}'.format(api_key)
    }

    r = requests.patch(
        'https://api.heroku.com/apps/{0}'.format(app_name),
        data={data_key: data_value},
        headers=headers
    )

    r.raise_for_status()


def main(argv):
    app_name = argv[0]
    api_key = argv[1]
    data_key = argv[2]
    data_value = argv[3]

    send_patch_request_to_heroku_app(app_name, api_key, data_key, data_value)


if __name__ == '__main__':
    main(sys.argv[1:4])
