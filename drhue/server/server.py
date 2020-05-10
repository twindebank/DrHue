from flask import Flask
from loguru import logger

from drhue.server.formatting import get_formatted_log, get_formatted_state
from drhue.state import State

PAGE = """
<div style="width=35%;float:left;overflow:scroll;height:100%">

{}

</div>

<div style="width:65%;float:right;height:100%;font-family:monospace;overflow-x:scroll;overflow-y:scroll;padding:10px;background:lightgrey">

{}

</div>
"""

s = State(read_only=True)


def start_server():
    logger.info("Starting webserver...")
    app = Flask(__name__)

    @app.route('/')
    def main():
        log_html = get_formatted_log()
        state_html = get_formatted_state(s)
        return PAGE.format(state_html, log_html)

    app.run(port=8080, host='0.0.0.0', threaded=True)
