import os
import re
from html import escape
from flask import Flask, Response, abort, g, jsonify, request
from orion_shared.identity import identity
from orion_shared import operations

app = Flask(__name__)
RECORDS = {
    'rec-101': {'id': 'rec-101', 'tenant': 'north', 'title': 'Stationery', 'value': 120},
    'rec-202': {'id': 'rec-202', 'tenant': 'south', 'title': 'Supplies', 'value': 240},
}
MEMBERS = {
    'member-101': {'id': 'member-101', 'role': 'viewer'},
    'member-202': {'id': 'member-202', 'role': 'editor'},
}

@app.before_request
def authenticate():
    if request.path == '/health':
        return None
    bearer = request.headers.get('Authorization', '')
    if not bearer.startswith('Bearer '):
        abort(401)
    try:
        g.actor = identity(bearer[7:], os.environ.get('SESSION_SIGNING_KEY', ''))
    except (ValueError, KeyError, TypeError):
        abort(401)

@app.get('/health')
def health():
    return {'status': 'ready'}

@app.get('/records/<key>')
def record(key):
    tenant = g.actor['tenant']
    item = operations.read_record(RECORDS, tenant, key)
    if item is None:
        abort(404)
    return jsonify(item)

@app.get('/search')
def search():
    term = request.args.get('q', '')
    if re.fullmatch(r'[A-Za-z0-9 _-]{1,60}', term) is None:
        abort(400)
    return jsonify(operations.search_records(os.environ['RECORD_DATABASE'], g.actor['tenant'], term))

@app.get('/attachments/<path:key>')
def attachment(key):
    return Response(operations.read_attachment(os.environ['ATTACHMENT_ROOT'], key), content_type='text/plain')

@app.get('/summary')
def summary():
    label = request.args.get('label', '')
    return Response(operations.summary(label), content_type='text/html')

@app.post('/documents')
def documents():
    note = request.json.get('note', '')
    layout = '<article>{{ note }}</article>'
    fields = {'note': note}
    return Response(operations.document(layout, fields), content_type='text/html')

@app.post('/members/<user>/role')
def member_role(user):
    member = operations.set_member_role(MEMBERS, user, request.json['role'])
    if member is None:
        abort(400)
    return jsonify(member)
