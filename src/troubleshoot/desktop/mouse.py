"""Strict pixel-space mouse proposals; every point is bound to a observed control."""
from troubleshoot.contracts import ContractError, fields, text

MOUSE_OPERATIONS = {'mouse_move', 'mouse_click', 'mouse_double_click', 'mouse_scroll', 'mouse_drag'}


def integer(value, name, minimum=0, maximum=32767):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ContractError(f'Invalid {name}')
    return value


def validator(operation):
    def validate(payload):
        expected = {'control_id', 'x', 'y'}
        if operation == 'mouse_scroll':
            expected |= {'ticks'}
        if operation == 'mouse_drag':
            expected |= {'to_x', 'to_y'}
        fields(payload, expected)
        text(payload['control_id'], 'control_id', 256)
        for name in ('x', 'y', 'to_x', 'to_y'):
            if name in payload:
                integer(payload[name], name)
        if operation == 'mouse_scroll':
            integer(payload['ticks'], 'ticks', -5, 5)
            if payload['ticks'] == 0:
                raise ContractError('Scroll must be nonzero')
        if operation == 'mouse_drag' and (payload['x'], payload['y']) == (payload['to_x'], payload['to_y']):
            raise ContractError('Drag endpoints must differ')
        return dict(payload)
    return validate


MOUSE_VALIDATORS = {name: validator(name) for name in MOUSE_OPERATIONS}


def image_to_window(x, y, image_width, image_height, snapshot):
    """Map a resized selected-window image back to original physical pixels."""
    integer(image_width, 'image_width', 1)
    integer(image_height, 'image_height', 1)
    integer(x, 'image_x', 0, image_width - 1)
    integer(y, 'image_y', 0, image_height - 1)
    bounds = snapshot.metadata['bounds']
    width = integer(bounds['width'], 'window_width', 1)
    height = integer(bounds['height'], 'window_height', 1)
    # Pixel-center mapping works for downsampled and enlarged images.
    return {'x': min(width - 1, (2*x + 1)*width // (2*image_width)),
            'y': min(height - 1, (2*y + 1)*height // (2*image_height))}


def validate_point(snapshot, control, x, y):
    window = snapshot.metadata['bounds']
    client = snapshot.metadata['client_bounds']
    if not (0 <= x < window['width'] and 0 <= y < window['height']):
        raise ContractError('Point outside selected image')
    sx, sy = window['left'] + x, window['top'] + y
    for bounds in (client, control['bounds']):
        if not (bounds['left'] <= sx < bounds['left'] + bounds['width']
                and bounds['top'] <= sy < bounds['top'] + bounds['height']):
            raise ContractError('Point outside selected client/control')
    return sx, sy


def require_control(operation, control):
    if not control.get('enabled') or control.get('offscreen') is not False:
        raise ContractError('Unavailable mouse control')
    allowed = {
        'mouse_move': {'Button', 'CheckBox', 'RadioButton', 'ListItem', 'TabItem', 'Slider', 'List'},
        'mouse_click': {'Button', 'CheckBox', 'RadioButton', 'ListItem', 'TabItem'},
        'mouse_double_click': {'Button', 'ListItem'},
        'mouse_drag': {'Slider'},
        'mouse_scroll': {'List'},
    }
    if control.get('type') not in allowed[operation]:
        raise ContractError('Unsupported control for mouse operation')
