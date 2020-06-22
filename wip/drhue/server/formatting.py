from path import Path


def get_formatted_log():
    log = Path('log.log').read_text().strip(' \n').split('\n')
    recent_first = '\n<br>'.join(reversed(log))
    return recent_first


def get_formatted_state(state):
    state.reload()
    nested = create_nested_dict_from_period_separated_keys(state)
    return nested_dict_to_html(nested)[5:]


def nested_dict_to_html(d, depth=0):
    html = ''
    for k, v in d.items():
        html += f"\n<br>{'&#160&#160' * depth} {k}: "
        if isinstance(v, dict):
            html += nested_dict_to_html(v, depth + 1)
        if isinstance(v, list):
            html += [nested_dict_to_html(x, depth + 1) for x in v]
        if isinstance(v, (str, int, float, bool)):
            html += f"<b>{str(v)}</b>"
    return html


def create_nested_dict_from_period_separated_keys(psk_dict):
    if any(isinstance(v, dict) for v in psk_dict.values()):
        raise ValueError("Values can't be dicts.")

    grouped = {}
    for k, v in psk_dict.items():
        d = grouped
        for i, nested_k in enumerate(k.split('.')):
            if i == len(k.split('.')) - 1:
                if not isinstance(d, dict) or nested_k in d:
                    raise ValueError('Nested keys overlap.')
                d[nested_k] = v
            else:
                d = d.setdefault(nested_k, {})
    return grouped
