import cvp
import dash
from dash import html, Input, Output, ALL

import pydicom
import os
import numpy as np
import time
from pydicom.pixel_data_handlers.util import convert_color_space
import cv2

filename1 = '../DICOM Scans/AO131541/M3LBMAB6'
ds1 = pydicom.dcmread(filename1)
video1 = ds1.pixel_array

filename2 = '../DICOM Scans/AO131541/M3FDA70K'
ds2 = pydicom.dcmread(filename2)
video2 = ds2.pixel_array


def prep_vid(pixel_array):
    # proper RGB presentation
    rgb = convert_color_space(pixel_array, "YBR_FULL", "RGB")
    processing_start = time.time()

    def resize_video(video, factor):
        """
        Resizes the video of format (nframes,height,width,3) to (nframes,height/factor,width/factor,3)
        """
        #print("resize_video called to resize ",video.shape," to (",video.shape[1]/factor,",",video.shape[2]/factor,")",sep="")
        nframes = video.shape[0]
        new_height = int(video.shape[1]/factor)
        new_width = int(video.shape[2]/factor)
        channels = video.shape[3]

        video_resized = np.zeros((nframes, new_height, new_width, channels))
        for frame in range(0, nframes):
            #print("At frame",frame,"of",nframes)
            image = video[frame, :, :, :]
            image_resized = cv2.resize(image, (new_width, new_height),  # fx=factor,fy=factor,
                                       interpolation=cv2.INTER_CUBIC)
            video_resized[frame, :, :, :] = image_resized
        return video_resized

    def rgb2rgba(rgb, A):
        # Transforms an RGB picture into an RGBA one (adds opacity channel)
        rows, cols, ch = rgb.shape
        rgba = A*np.ones(shape=(rows, cols, 4))
        for i in range(0, rows):
            for j in range(0, cols):
                for k in range(0, 4):
                    if (k == 3):
                        continue
                    rgba[i, j, k] = rgb[i, j, k]
        return rgba

    rgb_resized = resize_video(rgb, 2)
    video = rgb_resized
    image_pixels_list = [0]*video.shape[0]
    for i in range(0, video.shape[0]):
        rgbPic = video[i, :, :, :]
        rgbaPic = rgb2rgba(rgbPic, 255)
        flat_rgbaPic = rgbaPic.flatten(order='C')
        image_pixels_list[i] = flat_rgbaPic
    processing_end = time.time()
    processing_time = processing_end-processing_start
    print("Video processing time: ", processing_time)
    return image_pixels_list

def extract_type_index(str_dict):
    """
    Extracts the type and the index properties of the stringified 
    dictionary that is dash.callback_context.triggered[0]['prop_id']
    """
    #print("extract_type_index called with str_dict:",str_dict)
    # The stringified dictionary is in the format {"index":"index_value","type":"type_value"}.property
    # Find the id's type
    type_value_start = str_dict.index('"type":"') + len('"type":"')
    type_value_end = str_dict.find('"}')
    type_value = str_dict[type_value_start:type_value_end]
    #print("Type of trigger:",type_value)

    # Find the id's index
    index_value_start = str_dict.index('"index":"') + len('"index":"')
    index_value_end = str_dict.find('",')
    index_value = str_dict[index_value_start:index_value_end]
    #print("Index of trigger:",index_value)
    return (type_value,index_value)


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div([
            html.Button("change to vid1", id={"type":"change_vid_button","index":"1"}),
            html.Button("change to vid2", id={"type":"change_vid_button","index":"2"}),
            html.Button("change to vid1 for cvp2", id={"type":"change_vid_button_2","index":"1"},style={'margin':'0% 0% 0% 20%'}),
            html.Button("change to vid2 for cvp2", id={"type":"change_vid_button_2","index":"2"}),
        ]
        ),
        html.Div(
            cvp.cornerstoneVP(id='cvp'),
            id="cvp_div",
            style={"display":"inline-block","width":"45%",'margin':'2.5%'}
        ),
        html.Div(
            cvp.cornerstoneVP(id='cvp2'),
            id="cvp_div2",
            style={"display":"inline-block","width":"45%",'margin':'2.5%'}
        )
    ])

@app.callback(
    Output("cvp", "imagePixelsList"),
    Output("cvp", "dicomName"),
    Output("cvp", "dicomDateTime"),
    Output("cvp", "imageHeight"),
    Output("cvp", "imageWidth"),
    Output("cvp", "framerate"),
    Input({"type":'change_vid_button',"index":ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def serve_vid2(n_clicks):
    (type_value,index_value) = extract_type_index(dash.callback_context.triggered[0]['prop_id'])
    if (index_value == "1"):
        print("Serving vid1 to cvp1")
        imagePixelList = prep_vid(video1)
        return(imagePixelList,"M3LBMAB6","date of vid1",436/2,636/2,20)
    if (index_value == "2"):
        print("Serving vid2 to cvp1")
        imagePixelList = prep_vid(video2)
        return(imagePixelList,"M3FDA70K","date of vid2",436/2,636/2,30)

@app.callback(
    Output("cvp2", "imagePixelsList"),
    Output("cvp2", "dicomName"),
    Output("cvp2", "dicomDateTime"),
    Output("cvp2", "imageHeight"),
    Output("cvp2", "imageWidth"),
    Output("cvp2", "framerate"),
    Input({"type":'change_vid_button_2',"index":ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def serve_vid2(n_clicks):
    (type_value,index_value) = extract_type_index(dash.callback_context.triggered[0]['prop_id'])
    if (index_value == "1"):
        print("Serving vid1 to cvp2")
        imagePixelList = prep_vid(video1)
        return(imagePixelList,"M3LBMAB6","date of vid1",436/2,636/2,40)
    if (index_value == "2"):
        print("Serving vid2 to cvp2")
        imagePixelList = prep_vid(video2)
        return(imagePixelList,"M3FDA70K","date of vid2",436/2,636/2,60)

if __name__ == '__main__':
    app.run_server(debug=True)
