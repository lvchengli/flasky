from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Warning
from . import api
from .decorators import permission_required
from .errors import forbidden
import copy

@api.route('/warning')
def get_warnings():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)
    page = offset / limit + 1
    status = request.args.get('status', -1, type=int)
    level = request.args.get('level', -1, type=int)
    _dict = dict()
    if status != -1:
        _dict['status'] = status
    if level != -1:
        _dict['level'] = level
   
    pagination = Warning.query.filter_by(**_dict).paginate(
        page, per_page=limit,
        error_out=False)

    warnings = pagination.items
    warningList = copy.deepcopy(warnings)
    for i in warningList:
        i.handle_time = i.handle_time.isoformat(sep=' ')
        i.trigger_time = i.trigger_time.isoformat(sep=' ')

    return jsonify({
        'warnings': [warning.to_json() for warning in warningList],
        'total': pagination.total,
        '__name__': __name__,
        # 'offset': offset,
        # 'limit': limit,
        # 'page': page,
        # 'dict': isinstance(warnings,dict),
        # 'list': isinstance(warnings,list),
    })

@api.route('/warning/setstatus', methods=['POST'])
def set_warning_status():


    ids = request.json.get('ids')
    status = request.json.get('status')
    num = 3 if status == 'ignore' else 2

    Warning.query.filter(Warning.id.in_(ids)).update(dict(status=num), synchronize_session='fetch')

    return jsonify(request.json), 201

    # return jsonify(success=True)
