#!/usr/bin/env python3
from flask import url_for
from app import create_app

app = create_app()
with app.test_request_context():
    print("URL for dashboard.equipment_list:", url_for('dashboard.equipment_list'))
    print("URL for dashboard.index:", url_for('dashboard.index'))