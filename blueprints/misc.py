from flask import Blueprint, render_template

from utils import get_token_from_cache, login_required


misc_bp = Blueprint('misc_bp', __name__)


@misc_bp.route('/access_token', methods=['GET'])
@login_required
def get_access_token():
    token = get_token_from_cache(default_scope=True)
    return render_template('display.html', result=token,
                           api_name='Get Access Token',
                           tab_result_title=['access_token'],
                           tab_result_body=[[token['access_token']]])
