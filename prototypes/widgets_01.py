from datetime import datetime, timedelta
from bokeh.embed import components
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput
from bokeh.models import Slider
from bokeh.models.callbacks import CustomJS
from bokeh.layouts import column, row, layout

from flask import Flask
from flask import request

app = Flask(__name__)

widgets = {
    "datepicker_start":
        {'obj': None, 'value_field': 'value', 'arg_name': 'start_date', 'value': None,
         'title': "Start"},
    "datepicker_end":
        {'obj': None, 'value_field': 'value', 'arg_name': 'end_date',   'value': None,
         'title': "End"},
    "datepicker_left":
        {'obj': None, 'value_field': 'value', 'arg_name': 'left_date',  'value': None,
         'title': "Left"},
    "datepicker_right":
        {'obj': None, 'value_field': 'value', 'arg_name': 'right_date', 'value': None,
         'title': "Right"},
    "multiselect_1":
        {'obj': None, 'value_field': 'value', 'arg_name': 'ms1',        'value': None,
         'title': "Which One?", "options": [('a', '1'), ('b', '2'), ('c', '3'), ('d', '4')]},
    "input_1":
        {'obj': None, 'value_field': 'value', 'arg_name': 'in1',        'value': None,
         'title': "Your Name:"},
    "slider_1":
        {'obj': None, 'value_field': 'value', 'arg_name': 'sl1',        'value': 25,
         'title': "Your Age", 'start': 0, 'end': 99, 'step': 1},
}


def all_callback():
    """ a bokeh CustomJS that will be called when a widget is changed, that puts the
    value of the widget in the URL, for ALL widgets.
    :return: CustomJS
    """
    _parms = "{"
    _args = {}
    for key in widgets:
        w = widgets[key]
        if w['obj']:
            _parms += """'{}':{}.{},""".format(w["arg_name"], w["arg_name"], w["value_field"])
            _args[w["arg_name"]] = w["obj"]
    _parms += "}"
    #print(_parms)

    _code = """
            var params = {}
            var url = '/?' + encodeQueryData(params)
            window.location.replace(url);
        """.format(_parms)
    #print(_code)
    return CustomJS(args=_args, code=_code)


def common_js():
    text = """
    <script>
    function encodeQueryData(data) {
        let ret = [];
        for (let d in data)
            ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
        return ret.join('&');
    }
    </script>
    """
    return text


def start_end_datepicker(args, start, end):
    """ Handler for a start/end DatePicker pair of widgets
    :param args: dict URL args
    :param start: start DatePicker widget
    :param end: end DatePicker widget
    """

    d_yesterday = datetime.today() - timedelta(days=1)
    d_year_ago = datetime.today() - timedelta(days=365)

    # handle args related to which date picker the user last used
    if not start['arg_name'] in args:
        # the url did not have this value, assume first time being called
        min_end_date = datetime.today() - timedelta(days=1)
        curr_start_date = d_yesterday
    elif args[start['arg_name']].split(".")[0].isdigit():
        # when the end DatePicker is used, start Datepicker time comes as a epoch with ms
        curr_start_date = datetime.fromtimestamp(int(args[start['arg_name']].split(".")[0]) / 1000)
        min_end_date = curr_start_date
    else:
        curr_start_date = datetime.strptime(args[start['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
        curr_start_date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection
        min_end_date = curr_start_date

    if not end['arg_name'] in args:
        curr_end_date = datetime.today()
    elif args[end['arg_name']].split(".")[0].isdigit():
        curr_end_date = datetime.fromtimestamp(int(args[end['arg_name']].split(".")[0]) / 1000)
    else:
        curr_end_date = datetime.strptime(args[end['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
        curr_end_date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection

    start["value"] = curr_start_date
    start['obj'] = DatePicker(title=start["title"], min_date=d_year_ago, max_date=datetime.today(), value=curr_start_date)
    end["value"] = curr_end_date
    end['obj'] = DatePicker(title=end["title"], min_date=min_end_date, max_date=datetime.today(), value=curr_end_date)


def multi_select_handler(args, ms):
    """
    :param args: dict URL args
    :param ms: multiselect widget
    """
    selected = args.get(ms["arg_name"], "").split(",")
    ms["value"] = selected
    ms["obj"] = MultiSelect(options=ms["options"], value=selected, title=ms["title"])


def input_handler(args, input):
    """ INput text handler
    :param args: dict URL args
    :param input: input widget
    """
    input["value"] = args.get(input["arg_name"], input["value"])
    input["obj"] = TextInput(title=input["title"], value=input["value"])




def slider_handler(args, slider):
    """ Slider handler
    :param args: dict URL args
    :param input: input widget
    """
    _value = args.get(slider["arg_name"], slider["value"])
    if _value == 'NaN': _value = slider["value"]
    slider["value"] = int(_value)
    slider["obj"] = Slider(title=slider["title"], value=slider["value"], start=slider["start"], end=slider["end"],
                           step=slider["step"], callback_policy='mouseup')


def set_all_callbacks():
    for key in widgets:
        if widgets[key]["obj"] is not None:
            #if isinstance(widgets[key]["obj"], Slider): continue
            widgets[key]["obj"].callback = all_callback()


@app.route("/", methods=['GET'])
def test():
    text = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <link href="https://cdn.pydata.org/bokeh/release/bokeh-0.13.0.min.css" rel="stylesheet" type="text/css">
        <script src="https://cdn.pydata.org/bokeh/release/bokeh-0.13.0.min.js"></script>
        <link href="https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.13.0.min.css" rel="stylesheet" type="text/css">
        <script src="https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.13.0.min.js"></script>
        <meta charset="UTF-8">
    </head>
    <body>"""

    text += common_js()

    args = request.args.to_dict()
    print(args)

    start_end_datepicker(args, widgets["datepicker_start"], widgets["datepicker_end"])
    start_end_datepicker(args, widgets["datepicker_left"], widgets["datepicker_right"])

    multi_select_handler(args, widgets["multiselect_1"])

    input_handler(args, widgets["input_1"])

    slider_handler(args, widgets["slider_1"])

    set_all_callbacks()

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(column(widgets["datepicker_start"]["obj"],  widgets["datepicker_end"]["obj"]))
    doc_layout.children.append(widgets["multiselect_1"]["obj"])
    doc_layout.children.append(row(widgets["datepicker_left"]["obj"], widgets["datepicker_right"]["obj"]))
    doc_layout.children.append(row(widgets["input_1"]["obj"]))
    doc_layout.children.append(row(widgets["slider_1"]["obj"]))

    _script, _div = components(doc_layout)

    text += "{}{}".format(_script, _div)

    text += """</body></html>"""

    return text

app.run(host="0.0.0.0", port=6800)
