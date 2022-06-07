import requests
from flask import Blueprint, render_template, request

from utils import get_token_from_cache, get_graph_api_url, login_required


me_bp = Blueprint('me_bp', __name__)


def _to_gb(byte_val: int) -> str:
    return f'{byte_val/(1024**3):.1f} GB'


def _to_mb(byte_val: int) -> str:
    return f'{byte_val/(1024**2):.1f} MB'


@me_bp.route('/drives')
@login_required
def get_drives():
    def _proc_data(title, val):
        if title == 'owner':
            return val['user']['displayName']
        elif title == 'quota':
            return f'{_to_gb(val["used"])} / {_to_gb(val["total"])}'
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
        ret.append(_to_mb(remote_item['size']))
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


def _proc_drive_item_data(row):
    ret = []
    ret.append(row['id'])
    ret.append(row['name'])
    ret.append(_to_mb(row['size']))
    for item_type in ('folder', 'file', 'image', 'photo',
                      'audio', 'video', 'remoteItem'):
        if item_type in row:
            ret.append(item_type)
            break
    else:
        ret.append('unrecognized')
    return ret


@me_bp.route('/drive/item', methods=['GET'])
@login_required
def get_drive_item():
    query_method = request.args.get('query_method', None)
    if not query_method:
        return render_template('display_drive_items.html', result={})

    token = get_token_from_cache(default_scope=True)
    query_url = None
    if query_method == 'by_root':
        query_url = get_graph_api_url('/me/drive/root')
    elif query_method == 'by_path':
        query_url = get_graph_api_url(
            '/me/drive/root:' + request.args['path_val']
        )
    elif query_method == 'by_id':
        query_url = get_graph_api_url(
            '/me/drive/items/' + request.args['id_val']
        )

    graph_data = requests.get(
        query_url,
        headers={'Authorization': 'Bearer ' + token['access_token']}
    ).json()

    try:
        tab_result_title = ['id', 'name', 'size', 'type']
        tab_result_body = [_proc_drive_item_data(graph_data), ]
    except KeyError:
        tab_result_body = None

    return render_template('display_drive_items.html', result=graph_data,
                           api_name='/drive/item',
                           tab_result_title=tab_result_title,
                           tab_result_body=tab_result_body)


@me_bp.route('/drive/items', methods=['GET'])
@login_required
def get_drive_item_children():
    query_method = request.args.get('query_method', None)
    if not query_method:
        return render_template('display_drive_items.html', result={})

    token = get_token_from_cache(default_scope=True)
    query_url = None
    if query_method == 'by_root':
        query_url = get_graph_api_url('/me/drive/root/children')
    elif query_method == 'by_path':
        query_url = get_graph_api_url(
            '/me/drive/root:' + request.args['path_val'] + ':/children'
        )
    elif query_method == 'by_id':
        query_url = get_graph_api_url(
            '/me/drive/items/' + request.args['id_val'] + '/children'
        )

    graph_data = requests.get(
        query_url,
        headers={'Authorization': 'Bearer ' + token['access_token']}
    ).json()

    try:
        tab_result_title = ['id', 'name', 'size', 'type']
        tab_result_body = [_proc_drive_item_data(row) for row in graph_data['value']]
    except KeyError:
        tab_result_body = None

    return render_template('display_drive_items.html', result=graph_data,
                           api_name='/drive/item',
                           tab_result_title=tab_result_title,
                           tab_result_body=tab_result_body)
