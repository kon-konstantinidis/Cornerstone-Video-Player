# AUTO GENERATED FILE - DO NOT EDIT

export ''_cornerstonevp

"""
    ''_cornerstonevp(;kwargs...)

A cornerstoneVP component.
CornerstoneVP is the custom cornerstone 
dicom video player component, made for Dash.
It takes a list of images and displays them,
whilst giving additional controls and mouse 
tools to the user, per the cornerstone library.
Keyword arguments:
- `id` (String; required): The ID used to identify this component in Dash callbacks.
- `dicomDateTime` (String; optional): The date-time of the video to be displayed
- `dicomName` (String; optional): The DICOM filename of the video to be displayed
- `framerate` (Real; optional): Initially set framerate
- `imageHeight` (Real; optional): The height of the images in the imagePixelsList
- `imagePixelsList` (Array of Array of Realss; optional): A list of the image pixel 1D data array of all images
- `imageWidth` (Real; optional): The width of the images in the imagePixelsList
"""
function ''_cornerstonevp(; kwargs...)
        available_props = Symbol[:id, :dicomDateTime, :dicomName, :framerate, :imageHeight, :imagePixelsList, :imageWidth]
        wild_props = Symbol[]
        return Component("''_cornerstonevp", "cornerstoneVP", "cvp", available_props, wild_props; kwargs...)
end

