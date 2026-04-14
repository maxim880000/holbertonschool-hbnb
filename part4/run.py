import os
from flask import send_from_directory
from app import create_app

app = create_app()

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bases_files')


@app.route('/', defaults={'filename': 'index.html'})
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(FRONTEND, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
