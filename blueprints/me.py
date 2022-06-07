import requests
from flask import Blueprint, render_template

from utils import get_token_from_cache, get_graph_api_url, login_required


me_bp = Blueprint('me_bp', __name__)


@me_bp.route('/drives')
@login_required
def get_drives():
    def proc_data(title, val):
        if title == 'owner':
            return val['user']['displayName']
        elif title == 'quota':
            return f'{val["used"]} / {val["total"]}'
        else:
            return val

    token = get_token_from_cache(default_scope=True)
    graph_data = requests.get(
        get_graph_api_url('/drives'),
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    try:
        tab_result_title = ['driveType', 'id', 'owner', 'quota']
        tab_result_body = [
            [proc_data(title, row[title]) for title in tab_result_title]
            for row in graph_data['value']
        ]
    except KeyError:
        tab_result_body = None

    return render_template('display.html', result=graph_data,
                           api_name='drives',
                           tab_result_title=tab_result_title,
                           tab_result_body=tab_result_body)
