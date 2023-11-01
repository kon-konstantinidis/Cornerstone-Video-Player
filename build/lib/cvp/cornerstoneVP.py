# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class cornerstoneVP(Component):
    """A cornerstoneVP component.
CornerstoneVP is the custom cornerstone 
dicom video player component, made for Dash.
It takes a list of images and displays them,
whilst giving additional controls and mouse 
tools to the user, per the cornerstone library.

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- dicomDateTime (string; default undefined):
    The date-time of the video to be displayed.

- dicomName (string; default undefined):
    The DICOM filename of the video to be displayed.

- framerate (number; default undefined):
    Initially set framerate.

- imageHeight (number; default undefined):
    The height of the images in the imagePixelsList.

- imagePixelsList (list of list of numberss; default undefined):
    A list of the image pixel 1D data array of all images.

- imageWidth (number; default undefined):
    The width of the images in the imagePixelsList."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, imagePixelsList=Component.UNDEFINED, dicomName=Component.UNDEFINED, dicomDateTime=Component.UNDEFINED, imageHeight=Component.UNDEFINED, imageWidth=Component.UNDEFINED, framerate=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'dicomDateTime', 'dicomName', 'framerate', 'imageHeight', 'imagePixelsList', 'imageWidth']
        self._type = 'cornerstoneVP'
        self._namespace = 'cvp'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'dicomDateTime', 'dicomName', 'framerate', 'imageHeight', 'imagePixelsList', 'imageWidth']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(cornerstoneVP, self).__init__(**args)
