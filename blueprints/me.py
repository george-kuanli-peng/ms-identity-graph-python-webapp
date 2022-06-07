from unittest import result
import requests
from flask import Blueprint, render_template

from utils import get_token_from_cache, get_graph_api_url, login_required


me_bp = Blueprint('me_bp', __name__)


@me_bp.route('/drives')
@login_required
def get_drives():
    def _proc_data(title, val):
        if title == 'owner':
            return val['user']['displayName']
        elif title == 'quota':
            return f'{val["used"]/(1024**3):.1f} GB / {val["total"]/(1024**3):.1f} GB'
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
            [_proc_data(title, row[title]) for title in tab_result_title]
            for row in graph_data['value']
        ]
    except KeyError:
        tab_result_body = None

    return render_template('display.html', result=graph_data,
                           api_name='/drives',
                           tab_result_title=tab_result_title,
                           tab_result_body=tab_result_body)


@me_bp.route('/drive/sharedWithMe')
@login_required
def get_drive_shared_with_me():
    def _proc_data(row):
        ret = []
        ret.append(row['id'])
        remote_item = row['remoteItem']
        ret.append(remote_item['name'])
        ret.append(f"{remote_item['size']/(1024**2):.2f} MB")
        return ret

    token = get_token_from_cache(default_scope=True)
    graph_data = requests.get(
        get_graph_api_url('/me/drive/sharedWithMe'),
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    try:
        tab_result_title = ['id', 'name', 'size']
        tab_result_body = [_proc_data(row) for row in graph_data['value']]
    except KeyError:
        tab_result_body = None

    return render_template('display.html', result=graph_data,
                           api_name='/me/drive/sharedWithMe',
                           tab_result_title=tab_result_title,
                           tab_result_body=tab_result_body)
