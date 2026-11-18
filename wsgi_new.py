"""新版站点（每关一张地图）的 WSGI 入口，供 gunicorn / Render / PythonAnywhere 使用。"""
from app import app

if __name__ == '__main__':
    app.run(port=8080)
