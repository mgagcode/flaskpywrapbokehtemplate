#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
pywrapbokeh, Copyright (c) 2018, Martin Guthrie, All Rights Reserved
License: MIT License

"""

from datetime import datetime, timedelta
from bokeh.embed import components
from bokeh.models.callbacks import CustomJS
from bokeh.models import Slider, RangeSlider, AjaxDataSource
from bokeh.models.widgets.sliders import DateSlider
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput, Select
from bokeh.models.widgets.buttons import Button, Toggle, Dropdown
from bokeh.models.widgets import CheckboxButtonGroup, CheckboxGroup, RadioButtonGroup, RadioGroup, Tabs
from bokeh.models.widgets import Div

from dominate.tags import *
import dominate
from dominate.util import raw

import random
import string


class WrapBokeh(object):
    """ A class to wrap interactive widegts from bokeh.

    Notes:
    - if the boken widget is not interactive, then you don't need to use this, for example
      panels with tabs are not strictly interactive, ie no callback is needed
    """

    LEN_RANDOM_CLASS = 6

    class StubLogger(object):
        """ stubb out logger if none is provided"""
        # TODO: support print to console.  Issue here is flask app logger is tough to work around.
        def info(self, *args,**kwargs): pass
        def error(self, *args,**kwargs): pass
        def debug(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def critical(self, *args, **kwargs): pass

    logger = StubLogger()

    def __init__(self, url, logger=None):
        self.url = url
        if logger: self.logger = logger

        self.widgets = {}
        self.dom_doc = None

    def get_page_metrics(self):
        d = self.dom_doc

        with d.body:
            js = """
            function postAndRedirect(url, postData, callerWidget) {
                var postFormStr = "<form id='virtualForm' method='POST' action='" + url + "'>";
                postFormStr += "<input type='hidden' name='callerWidget' value='" + callerWidget + "'></input>";
                postFormStr += "<input type='hidden' name='windowWidth' value='" + window.innerWidth + "'></input>";
                postFormStr += "<input type='hidden' name='windowHeight' value='" + window.innerHeight + "'></input>";
                postFormStr += "<input type='hidden' name='windowUrl' value='" +url + "'></input>";
             
                postFormStr += "</form>";
                //alert(postFormStr);
                //alert(postAndRedirect.caller);  // probably not useful
                
                var formElement = $(postFormStr);
            
                $('body').append(formElement);
                $('#virtualForm').submit();
            }   
            
            function postAndRedirectWrapper() {
                postAndRedirect(window.location.href, {}, 'windowResize' )
            }

            window.addEventListener("resize", postAndRedirectWrapper);
            window.dispatchEvent(new Event('resize'));
            """
            script(raw(js))

        return "{}".format(d)

    def dominate_document(self, title="pywrapBokeh", bokeh_version='0.13.0'):
        """ Create dominate document, see https://github.com/Knio/dominate

        Populates the required bokeh/jquery links
        Sets up common javascript

        The dominate document is returned, but if you don't need to use it, just ignore it

        :param title: title string
        :param bokeh_version: version
        :return: dominate document
        """
        d = dominate.document(title=title)
        with d.head:
            link(href="https://cdn.pydata.org/bokeh/release/bokeh-{bokeh_version}.min.css".format(bokeh_version=bokeh_version),
                 rel="stylesheet",
                 type="text/css")
            script(src="https://cdn.pydata.org/bokeh/release/bokeh-{bokeh_version}.min.js".format(bokeh_version=bokeh_version))
            link(href="https://cdn.pydata.org/bokeh/release/bokeh-widgets-{bokeh_version}.min.css".format(bokeh_version=bokeh_version),
                 rel="stylesheet",
                 type="text/css")
            script(src="https://cdn.pydata.org/bokeh/release/bokeh-widgets-{bokeh_version}.min.js".format(bokeh_version=bokeh_version))
            link(href="https://cdn.pydata.org/bokeh/release/bokeh-tables-{bokeh_version}.min.css".format(bokeh_version=bokeh_version),
                 rel="stylesheet",
                 type="text/css")
            script(src="https://cdn.pydata.org/bokeh/release/bokeh-tables-{bokeh_version}.min.js".format(bokeh_version=bokeh_version))

            script(src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js")

            meta(charset="UTF-8")

        with d.body:
            js = """
            function postAndRedirect(url, postData, callerWidget) {
                var postFormStr = "<form id='virtualForm' method='POST' action='" + url + "'>";
            
                for (var key in postData) {
                    if (postData.hasOwnProperty(key)) {
                        postFormStr += "<input type='hidden' name='" + encodeURIComponent(key) + "' value='" + unescape(encodeURIComponent(postData[key])) + "'></input>";
                    }
                }
                // add the widget that triggers the post
                postFormStr += "<input type='hidden' name='callerWidget' value='" + callerWidget + "'></input>";
                postFormStr += "<input type='hidden' name='windowWidth' value='" + window.innerWidth + "'></input>";
                postFormStr += "<input type='hidden' name='windowHeight' value='" + window.innerHeight + "'></input>";
                postFormStr += "<input type='hidden' name='windowUrl' value='" +url + "'></input>";
             
                postFormStr += "</form>";
                //alert(postFormStr);
                //alert(postAndRedirect.caller);  // probably not useful
                
                var formElement = $(postFormStr);
            
                $('body').append(formElement);
                $('#virtualForm').submit();
            }      
            
            function postAndRedirectWrapper() {
                // dummy prevents thinking that landing on URL for first time, resize 
                // is caused by user after landing on the page
                postAndRedirect(window.location.href, {'dummy': 0}, 'windowResize' )
            }
            
            window.addEventListener("resize", postAndRedirectWrapper);
               
            """
            script(raw(js))

        self.logger.info("created dominate document")
        self.logger.debug(d)
        self.dom_doc = d
        return d

    def _make_args_parms(self):
        _parms_all = ""
        _args_all = {}
        for w_name, w_params in self.widgets.items():
            if w_params.get("obj", False):

                if isinstance(w_params.get("obj"), AjaxDataSource):
                    # AjaxDataSource doesn't have a 'value' field that can be pulled, so for
                    # all other objects, skip including its status. AjaxDataSource.selected.js_on_change()
                    # is set in _set_all_callbacks()
                    continue

                _parms_all += """'{name}':{name}.{value},""".format(name=w_name, value=w_params["value_field"])
                _args_all[w_name] = w_params["obj"]

        self.logger.debug(_parms_all)

        _code_all = """
               var params = {};
               postAndRedirect('{}', params, 'callerWidget');
        """.format(_parms_all, self.url)
        self.logger.debug(_code_all)
        return _args_all, _parms_all

    def _set_all_callbacks(self):
        """ attach a bokeh CustomJS that will be called when a widget is changed, that puts the
        value of the widget in the URL, for ALL widget callbacks.
        """
        _args, _parms_all = self._make_args_parms()

        for key in self.widgets:
            if self.widgets[key]["obj"] is not None and self.widgets[key]["pywrap_trigger"]:

                if isinstance(self.widgets[key]["obj"], AjaxDataSource):
                    # AjaxDataSource, and probably ColumnDataSource, get a different
                    # JS event handler to access the row of data from the user selection
                    # Note that _parms_all is included so that all other widget values are
                    # included in the AjaxDataSource event
                    _code_all = """var idx = source.selected["1d"]["indices"][0];"""

                    if self.widgets[key]["value_field"] is not None:
                        _code_all +="""var params = {{ {} '{}': idx + ',' + source.data["{}"][idx] }};""".format(_parms_all,
                                                                                                                 key,
                                                                                                                 self.widgets[key]["value_field"])
                    else:
                        _code_all +="""var params = {{ {} '{}': idx }};""".format(_parms_all, key)

                    _code_all += """postAndRedirect('{}', params, '{}');""".format(self.url, key)

                    __args = {**_args, **dict(source=self.widgets[key]["obj"])}

                    callback = CustomJS(args=__args, code=_code_all)
                    self.widgets[key]["obj"].selected.js_on_change('indices', callback)

                else:
                    _code_all = """
                           var params = {{ {} }};
                           postAndRedirect('{}', params, '{}');
                    """.format(_parms_all, self.url, key)
                    self.widgets[key]["obj"].callback = CustomJS(args=_args, code=_code_all)

    def _set_slider(self, slider, name, value, args):
        """ Slider, value is a string of an integer, set int
        :param name:
        :param value:
        """
        if value == 'NaN':
            _value = slider.value
        if isinstance(value, str):
            _value = float(value) if "." in value else int(value)
        slider.value = _value
        return args

    def _set_rangeslider(self, slider, name, value, args):
        """ Slider, value is a string of an integer, set int
        :param name:
        :param value:
        """
        _values = value.split(",")
        for idx, value in enumerate(_values):
            if value == 'NaN':
                _value = slider.value
            if isinstance(value, str):
                _value = float(value) if "." in value else int(value)
            _values[idx] = _value
        slider.value = _values
        return args

    def _set_datep(self, datep, name, value, args):
        # the datepicker will return an epoch if it wasn't the callback trigger
        # and it returns a 'Mon Jun 18 2018' format if it was the trigger, handle both...
        # And note there is a one day off bug that is also handled.
        if value.split(".")[0].isdigit():  # epoch
            date = datetime.fromtimestamp(int(value.split(".")[0]) / 1000)
            # TODO: set hours and minutes to 0:0
            args[name] = date
        else:  # string date 'Mon Jun 18 2018'
            date = datetime.strptime(value, "%a %b %d %Y")
            args[name] = date
            date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection

        datep.value = date
        self.widgets[name]["value"] = date
        return args

    def _set_dateslider(self, dateslider, name, value, args):
        if value.split(".")[0].isdigit():  # epoch
            date = datetime.fromtimestamp(int(value.split(".")[0]) / 1000)
            # TODO: set hours and minutes to 0:0
            args[name] = date
        else:  # string date 'Mon Jun 18 2018'
            date = datetime.strptime(value, "%a %b %d %Y")
            args[name] = date
            date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection

        dateslider.value = date
        self.widgets[name]["value"] = date
        return args

    def _set_multisel(self, multisel, name, value, args):
        cache = multisel.value

        if value in cache: cache.remove(value)
        else: cache.append(value)

        args[name] = cache
        self.widgets[name]["value"] = cache
        multisel.value = cache
        return args

    def _set_button(self, b, name, value, args):
        """ Button handler
        - Button doesn't have an value attribute, but we create one.
        - args["button_name"] is set to True if the user pressed the button
        """
        value = False
        if args.get('callerWidget', False):
            if args['callerWidget'] == name:
                value = True

        self.widgets[name]["value"] = value
        args[name] = value
        return args

    def _set_toggle(self, toggle, name, value, args):
        value = False
        if args.get('callerWidget', False):
            if args['callerWidget'] == name:
                if not self.widgets[name]["value"]:
                    value = True

        toggle.active = value
        self.widgets[name]["value"] = value
        args[name] = value
        return args

    def _set_dropdown(self, dropdown, name, value, args):
        dropdown.value = value
        self.widgets[name]["value"] = value
        return args

    def _set_select(self, sel, name, value, args):
        self.widgets[name]["value"] = value
        sel.value = value
        return args

    def _set_cbbg(self, cbbg, name, value, args):
        active = [int(x) if x else None for x in value.split(",")]
        self.widgets[name]["value"] = active
        cbbg.active = active
        return args

    def _set_rbg(self, rbg, name, value, args):
        if value == 'NaN':
            _value = rbg.value
        if isinstance(value, str):
            _value = float(value) if "." in value else int(value)
        self.widgets[name]["value"] = _value
        rbg.active = _value
        return args

    def _set_textinput(self, ti, name, value, args):
        if value == None: value = ti.placeholder
        self.widgets[name]["value"] = value
        ti.value = value
        return args

    def _set_ajaxdatasource(self, ads, name, value, args):
        self.widgets[name]["value"] = value
        return args

    def add(self, name, widget, other=None):
        """ Add a bokeh widget
        API
          WrapBokeh.add( <name_of_widget>, <bokeh API>(..., [css_classes=['sel_fruit']]))

        Notes:
          1) if you want to affect widget properties (color, font size, etc) you need to set css_classes

        :param name: unique name (string)
        :param widget: bokeh widget
        :return: True on success, False otherwise
        """

        if self.widgets.get(name, False):
            self.logger.error("{} widget name duplicate".format(name))
            return False

        pywrap_update_value = False
        pywrap_trigger = True

        if isinstance(widget, (Slider, )):
            value_field = 'value'
            setter = self._set_slider
            value = widget.value
            # TODO: ensure that widget.callback_policy = 'mouseup'
        elif isinstance(widget, (RangeSlider, )):
            value_field = 'value'
            setter = self._set_rangeslider
            value = widget.value
            # TODO: ensure that widget.callback_policy = 'mouseup'
        elif isinstance(widget, (DatePicker, )):
            value_field = 'value'
            setter = self._set_datep
            value = widget.value
        elif isinstance(widget, (DateSlider, )):
            value_field = 'value'
            setter = self._set_dateslider
            value = widget.value
        elif isinstance(widget, (MultiSelect, )):
            value_field = 'value'
            setter = self._set_multisel
            value = widget.value
        elif isinstance(widget, (Button, )):
            value_field = None
            setter = self._set_button
            value = None
            pywrap_update_value = True
        elif isinstance(widget, (Toggle, )):
            value_field = "active"
            setter = self._set_toggle
            value = widget.active
        elif isinstance(widget, (Dropdown, )):
            value_field = 'value'
            setter = self._set_dropdown
            value = widget.value
        elif isinstance(widget, (Select, )):
            value_field = 'value'
            setter = self._set_select
            value = widget.value
        elif isinstance(widget, (CheckboxButtonGroup, CheckboxGroup, )):
            value_field = 'active'
            setter = self._set_cbbg
            value = widget.active
        elif isinstance(widget, (RadioButtonGroup, RadioGroup, )):
            value_field = 'active'
            setter = self._set_rbg
            value = widget.active
        elif isinstance(widget, (TextInput, )):
            value_field = 'value'
            setter = self._set_textinput
            value = widget.value
            pywrap_update_value = True
            pywrap_trigger = False
        elif isinstance(widget, (AjaxDataSource, )):
            if other is None:
                self.logger.info("AjaxDataSource will return idx of user selected row")
                # its also possible to get the data column value by specifying the name
                # of the field to return in 'other'
            value_field = other
            value = None
            setter = self._set_ajaxdatasource
            pywrap_update_value = False
        else:
            self.logger.error("4Unsupported widget class of name {}".format(name))
            return False

        self.widgets[name] = {
            'obj': widget,
            'value': value,
            'value_field': value_field,
            'setter': setter,
            # internal stuff
            'pywrap_trigger': pywrap_trigger, # won't cause a JS trigger
                                              # needed for TextInput() items
            'pywrap_update_value': pywrap_update_value,
        }
        return True

    def process_req(self, req):
        """ Updates the state of every widget based on the values of each widget in args
        - sets the callback for each widget
        :param args: dict of every widget value by name
        :return args dict, redirect render
        """
        if req.method == "POST": args = req.form.to_dict()
        else: args = {}
        self.logger.debug("--> {}".format(args))

        # if args is false/{}, this is the first time landing
        # on this page, and we want to trigger get_page_metrics()
        # which will get page metrics and come right back here
        if not args: return args, self.get_page_metrics()

        # which ever widget the user touched, run its handler
        # so that its args can be correct
        w_name = args.get('callerWidget', None)
        if w_name and w_name in self.widgets:
            w_value = args.get(w_name, None)
            w = self.widgets[w_name]
            args = w["setter"](w["obj"], w_name, w_value, args)

        # scan for items that need a manual value update, !TextInput!
        for key in self.widgets:
            if self.widgets[key].get("obj", None):
                if self.widgets[key].get("pywrap_update_value", False):
                    w_value = args.get(key, None)
                    widget = self.widgets[key]
                    args = widget["setter"](widget["obj"], key, w_value, args)

        self.logger.info("<-- {}".format(args))
        return args, None

    def init(self):
        """ init - call this after all the widgets on a page have been created
        """
        self._set_all_callbacks()

    def get(self, name):
        """ get bokeh object by name
        - client can access bokeh obj methods and variables
        :param name:
        :return: bokeh object
        """
        if not self.widgets.get(name, False):
            self.logger.error("{} widget not found".format(name))
            return Div(text="""<p style="color:red;">!!Missing Widget {}!!</p>""".format(name))
        return self.widgets[name]["obj"]

    def exist(self, name):
        if self.widgets.get(name, False): return True
        return False

    def get_value(self, name):
        """ return the value of a bokeh object
        - in general this is not needed because the page 'args' have the same value
        :param name: name of widget
        :return: None on error, otherwise widget value/active/cached
        """
        if not self.widgets.get(name, False):
            self.logger.error("{} widget not found".format(name))
            return None

        if isinstance(self.widgets[name]["obj"], (Slider, RangeSlider, DatePicker, MultiSelect,
                                                  Dropdown, Select, TextInput, )):
            return self.widgets[name]["obj"].value
        elif isinstance(self.widgets[name]["obj"], (Button, AjaxDataSource, )):
            # use cached value
            return self.widgets[name]["value"]
        elif isinstance(self.widgets[name]["obj"], (Toggle, CheckboxButtonGroup, CheckboxGroup,
                                                    RadioButtonGroup, RadioGroup, )):
            return self.widgets[name]["obj"].active

        self.logger.error("Unsupported widget class of name {} type {}".format(name, type(self.widgets[name]["obj"])))
        return None

    def render_div(self, layout, cls=None):
        """ add a div section to the dominate document

        #Adding a div with class style,
        doc_layout = layout(sizing_mode='scale_width')
        doc_layout.children.append(Div(text="<h1>Your Stuff Goes Here...</h1>"))
        ...
        w.add_css("test", {'div': {'background-color': '#98FB98'}})
        w.render_div(doc_layout, cls="test")

        :param layout: bokeh layout object
        :param cls: class name of div, so that a style can be applied
        """
        if self.dom_doc is None:
            self.logger.error("Dominate doc is None, call dominate_document() first")
            return "<p>Error: Dominate doc is None, call dominate_document() first</p>"

        if cls is None:
            cls = ''.join(random.choices(string.ascii_uppercase + string.digits, k=self.LEN_RANDOM_CLASS))

        _script, _div = components(layout)
        d = div(cls=cls)
        with d:
            raw(_script)
            raw(_div)
        self.dom_doc.add(d)

    def render_incremental(self, layout):
        if self.dom_doc is None:
            self.logger.error("Dominate doc is None, call dominate_document() first")
            return "<p>Error: Dominate doc is None, call dominate_document() first</p>"

        _script, _div = components(layout)
        self.dom_doc.body += raw(_script)
        self.dom_doc.body += raw(_div)

    def render_append_html(self, dominate_html_item):
        self.dom_doc.body += dominate_html_item

    def render_fini(self):
        return "{}".format(self.dom_doc)

    def render(self, layout, footnote=None):
        """ render the layout in the current dominate document
        :param layout: bokeh layout object
        :return: dominate document with bokeh objects rendered within it
        """
        if self.dom_doc is None:
            self.logger.error("Dominate doc is None, call dominate_document() first")
            return "<p>Error: Dominate doc is None, call dominate_document() first</p>"

        _script, _div = components(layout)
        self.dom_doc.body += raw(_script)
        self.dom_doc.body += raw(_div)
        if footnote: self.dom_doc.body += footnote
        return "{}".format(self.dom_doc)

    def add_css(self, name, css_dict):
        """ Add css style modifiers for a named widget
        example
          widgets.add_css("sel_state", {'select' :{'background-color': '#F08080'}})

        Using this API may require experimentation.  Using the browser, 'inspect'
        the page and try and find the widget style properties and modify them.

        :param name:
        :param css_dict: { 'attribute': 'value', ... }
        """
        if self.dom_doc is None:
            self.logger.error("Dominate doc is None, call dominate_document() first")
            return

        if not isinstance(css_dict, dict) or css_dict is None:
            self.logger.error("css_dict argument is invalid")
            return

        attrs = ""
        for item, properties in css_dict.items():
            for key, value in properties.items():
                attrs += "{}: {} !important; ".format(key, value)

            _css = """.{} {} {{ {} }}""".format(name, item, attrs)
            with self.dom_doc.body:
                style(raw(_css))

    def dom_doc(self):
        return self.dom_doc