from flask import Flask
from loguru import logger
from path import Path

from drhue.state import State

PAGE = """
<div style="width=50%;float:left;overflow:scroll;height:100%">
{}
</div>

<div style="width:50%;float:right;height:100%;font-family:monospace;overflow:scroll;padding:10px;background:lightgrey">
{}
</div>
"""


def get_formatted_log():
    log = Path('log.log').read_text()
    recent_first = '\n<br>'.join(reversed(log.split('\n')))
    return recent_first


def get_formatted_state():
    s = State()
    strs = [f"<b>{k}</b>: {v}" for k, v in s.items()]
    return '\n<br>'.join(strs)


def start_server():
    logger.info("Starting webserver...")
    app = Flask(__name__)

    @app.route('/')
    def main():
        return PAGE.format(get_formatted_state(), get_formatted_log())

    app.run(port=8080, host='0.0.0.0')
