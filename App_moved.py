import matplotlib.pylab as plt
import base64
import io
import dash
from dash import Dash, html, Input, Output, dcc, State, ALL
from dash.exceptions import PreventUpdate
import datetime
import numpy as np
import pydicom
import matplotlib

matplotlib.use('Agg')  # non-GUI backend to avoid annoying warning message
import dash_auth
from pydicom.pixel_data_handlers.util import convert_color_space
from flask import request
import os
import cvp


def serve_homepage_layout():
    layout = html.Div([
        # App Header (top)
        html.Header(children=[
            dcc.Interval(id="interval_component"),
            html.Div(
                    children=serve_datetime(),  # Date and time text
                    id="date_time",
                    style={'width': '20%', 'height': '100%', 'display': 'inline-block',
                           'background-color': 'yellow'}
                    ),
            html.H1(
                children="ECHO Web App",
                style={'width': '60%', 'height': '100%', 'display': 'inline-block', 'textAlign': 'center', 'background-color': 'red', 'margin': '0px', 'vertical-align': 'top'})
        ],
            style={'height': '10%', 'background-color': '#5A02CB'}
        ),

        # Imported Scans section (left)
        html.Div(children=[
            html.H3("Imported Scans",
                    style={'height': '3%', 'textAlign': 'center', 'margin': '1%', 'padding': '0px'}),
            html.H4("Scan Count: 0", id="scan_count",
                    style={'height': '2%', 'textAlign': 'center', 'margin': '0.5%', 'padding': '0px'}),
            html.Hr(),
            serve_scan_thumbnails(),
            html.Button('Clear All Scans', id={'type':'clear_all_scans_button', 'index':'1'},
                        style={'width': '60%', 'height': '5%', 'textAlign': 'center', 'margin': '0% 20%', 'background-color': '#130665', 'color': '#FFFFFF'}),
            html.Button('Upload ECHO Scan', id={'type': 'hidden_div_button', 'index': 'upload_button'},
                        style={'width': '80%', 'height': '7%', 'textAlign': 'center', 'margin': '2% 10% 1%', 'background-color': '#130665', 'color': '#FFFFFF'})
        ],
            style={'width': '20%', 'height': '90%',
                   'display': 'inline-block', 'background-color': '#C4C4C4'}
        ),

        # Scan playback section (middle)
        html.Div(children="Scan playback", id='scan_playback_section', style={
            'width': '60%', 'height': '90%', 'display': 'inline-block', 'vertical-align': 'top', 'background-color': '#130665'}),

        # User Options section (right)
        html.Div([
            html.Button("Patient Info",
                        id={'type': 'hidden_div_button',
                            'index': 'patient_info_button'},
                        style={'width': '80%', 'height': '5%', 'margin': '5% 10%',
                               'textAlign': 'center', 'background-color': '#130665', 'color': '#FFFFFF'}
                        ),
            html.Button("LVEF Estimation",
                        id={'type': 'hidden_div_button', 'index': 'LVEF_button'},
                        style={'width': '80%', 'height': '5%', 'margin': '45% 10% 5%',
                               'textAlign': 'center', 'background-color': '#130665', 'color': '#FFFFFF'}
                        ),
            html.Button("LVGLS Estimation",
                        id={'type': 'hidden_div_button',
                            'index': 'LVGLS_button'},
                        style={'width': '80%', 'height': '5%', 'margin': '5% 10%',
                               'textAlign': 'center', 'background-color': '#130665', 'color': '#FFFFFF'}
                        )
        ],
            id='options_section',
            style={'width': '20%', 'height': '90%', 'display': 'inline-block', 'background-color': 'purple', 'vertical-align': 'top'}),

        # Extra Div for Upload/Analysis Windows
        # This Div is in the middle of the screen, but invisible - always underlying until used
        html.Div([],
                 id='hidden_div',
                 style={'width': '70%', 'height': '85%', 'background-color': 'black', 'position': 'fixed', 'top': '12%', 'left': '15%', 'z-index': '-1'})
    ],
        style={'height': '660px', 'background-color': 'black'}, id='app_div')
    return layout


def serve_datetime():
    current_time = datetime.datetime.now()

    date_string = "Date: " + str(current_time.day) + "/" + \
        str(current_time.month) + "/" + str(current_time.year)

    # Pad with an extra 0 the hour, minute and second strings (in case of single digit values)
    hour_string = str(current_time.hour)
    if (len(hour_string) == 1):
        hour_string = "0" + hour_string

    minute_string = str(current_time.minute)
    if (len(minute_string) == 1):
        minute_string = "0" + minute_string

    second_string = str(current_time.second)
    if (len(second_string) == 1):
        second_string = "0" + second_string

    time_string = "Time: " + hour_string + ":" + minute_string + ":" + second_string

    date_component = html.H2(children=date_string, style={
                             'height': '30px', 'textAlign': 'left', 'margin': '0px'})
    time_component = html.H2(children=time_string, style={
                             'height': '30px', 'textAlign': 'left', 'margin': '0px'})
    return (date_component, time_component)


def serve_upload_layout():
    upload_window = html.Div([
        # Header
        html.Header([
            html.Div([], style={'width': '10%', 'height': '100%',
                                'margin': '0px', 'display': 'inline-block'}),
            html.H2("Import ECHO Scan", style={'width': '80%', 'height': '100%', 'margin': '0px',
                                               'textAlign': 'center', 'vertical-align': 'top', 'display': 'inline-block'}),
            html.Button("X", id={'type': 'hidden_div_button', 'index': 'upload_window_X_button'}, style={
                'width': '10%', 'height': '100%', 'margin': '0px', 'vertical-align': 'top'}),
        ], style={'width': '100%', 'height': '15%', 'background-color': '#5A02CB'}),
        # Upload Window Body
        html.Div(
            [
                html.H3("Upload a DICOM file from your files",
                        style={'textAlign': 'center',
                               'margin': '0px', 'padding': '3% 0% 1%'}
                        ),
                html.H4("You can choose multiple files at once",
                style={'textAlign': 'center',
                        'margin': '0px', 'padding': '1% 0% 1%'}
                ),
                dcc.Upload([
                    "Drag and Drop a file here or ",
                    html.A("Select From Your Files", style={
                           'font-weight': 'bold', 'text-decoration-line': 'underline', 'cursor': 'pointer'})
                ],
                    style={
                    'width': '60%',
                    'height': '50%',
                    'lineHeight': '600%',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '2% 20%'},
                    multiple=True, # Allow multiple files to be uploaded
                    id={'type':'file_upload', 'index':1}
                ),
                html.H4("Do not close this window before the uploads are complete",
                style={'textAlign': 'center',
                        'margin': '0px', 'padding': '0% 0% 0%'}
                )
            ], style={'width': '100%', 'height': '90%', 'background-color': '#C4C4C4', 'margin': '0px'}
        )
    ], style={'width': '40%', 'height': '40%', 'background-color': 'white', 'position': 'fixed', 'top': '20%', 'left': '30%'})
    return upload_window


def serve_scan_thumbnails():
    thumbnails = html.Div([
        # Option 1
        html.Button([
            html.Img(src=app.get_asset_url('echo_scan_1.png'),
                     style={'width': '100%', 'height': '100%'}),
            html.H4("(Opt.1) 1. 16/4/2022 14:55:23",
                    style={'margin': '0%', 'direction': 'ltr'})
        ], style={'witdh': '70%', 'height': '35%', 'margin': '2%'}, id={'type': 'scan_playbutton', 'index': 1}
        ),
        # Option 2
        html.Div([
            html.Button(
                html.Img(src=app.get_asset_url('echo_scan_2.png'),
                         style={'width': '100%', 'height': '100%'}),
                style={'height': '90%'}, id={'type': 'scan_playbutton', 'index': 2}),
            html.H4("(Opt.2) 2. 16/4/2022 15:21:58",
                    style={'height': '10%', 'margin': '0%', 'direction': 'ltr'})
        ], style={'width': '100%', 'height': '40%', 'margin': 'auto', 'padding-top': '3%'}),
        # Option 2 again
        html.Div([
            html.Button(
                html.Img(src=app.get_asset_url('echo_scan_2.png'),
                         style={'width': '100%', 'height': '100%'}),
                style={'height': '90%'}, id={'type': 'scan_playbutton', 'index': 3}),
            html.H4("(Opt.2) 3. 16/4/2022 15:31:01",
                    style={'height': '10%', 'margin': '0%', 'direction': 'ltr'})
        ], style={'width': '100%', 'height': '40%', 'margin': 'auto', 'padding-top': '3%'})
    ],
        id="scan_thumbnails",
        style={'height': '80%', 'textAlign': 'center', 'margin': '2.5%', 'padding': '0px', 'background-color': 'white', 'overflow': 'scroll', 'direction': 'rtl'})
    return html.Div([], id="scan_thumbnails",
                    style={'height': '75%', 'textAlign': 'center', 'margin': '2.5% 2.5% 0.5% 2.5%', 'padding': '0px', 'background-color': 'white', 'overflow': 'scroll', 'direction': 'rtl'})  # thumbnails


def serve_patient_info_form():
    window_children = [
        html.H2("Add Patient Info", style={
                'margin': '0%', 'padding': '0%', 'textAlign': 'center', 'width': '100%', 'height': '5%', 'text-decoration-line':'underline'}),
        
        # Patient Detail (left)
        html.Div(
            [
                 html.H3("General Information", style={'width': '100%', 'height': '5%','margin': '0', 'background-color': 'blue','textAlign':'center'}),
                # margin: top right bottom left
                # First Name
                html.Div([
                    html.P(
                        "First Name: ", 
                        style={'width': '35%', 'height': '100%', 'display': 'inline-block',
                       'margin': '0% 1%', 'background-color': 'blue','vertical-align': 'top',}#'vertical-align': 'top', 'font-size': '100%', 'padding-top':'1.2%'
                    ),
                    dcc.Input(
                        placeholder="Enter patient's name", 
                        style={'width': '59%', 'height': '100%', 'display': 'inline-block',
                          'margin': '0% 1%', 'padding': '0%','background-color': 'yellow'} # , 'font-size': '80%'
                    )
                ], style = {'width':'80%','height':'8%','margin':'2% 8% 0% 2%','background-color':'red'}),
                # Last Name
                html.Div([
                    html.P(
                        "Last Name: ", 
                        style={'width': '35%', 'height': '100%', 'display': 'inline-block',
                       'margin': '0% 1%', 'background-color': 'blue','vertical-align': 'top','padding-top':'1.2%'}#'vertical-align': 'top', 'font-size': '100%'
                    ),
                    dcc.Input(
                        placeholder="Enter patient's surname", 
                        style={'width': '55%', 'height': '100%', 'display': 'inline-block',
                          'margin': '0% 1%', 'padding': '0','background-color': 'yellow'} # , 'font-size': '80%'
                    )
                ], style = {'width':'80%','height':'8%','margin':'2% 8% 0% 2%','background-color':'red'}),
                # Date Of Birth
                html.Div([
                    html.P(
                        "Date of Birth: ", 
                        style={'width': '35%', 'height': '100%', 'display': 'inline-block',
                       'margin': '1%', 'background-color': 'blue','vertical-align': 'top','padding-top':'1.2%'}#'vertical-align': 'top', 'font-size': '100%'
                    ),
                    dcc.Input(
                        placeholder="Enter patient's birthday", 
                        style={'width': '55%', 'height': '100%', 'display': 'inline-block',
                          'margin': '1%', 'padding': '0','background-color': 'yellow','vertical-align': 'bottom'} # , 'font-size': '80%'
                    )
                ], style = {'width':'80%','height':'10%','margin':'2% 8% 0% 2%','background-color':'red'}),
                # Gender
                html.Div([
                    html.P(
                        "Gender: ", 
                        style={'width': '35%', 'height': '100%', 'display': 'inline-block',
                       'margin': '1%', 'background-color': 'blue','vertical-align': 'top','padding-top':'1.2%'}#'vertical-align': 'top', 'font-size': '100%'
                    ),
                    dcc.Input(
                        placeholder="Enter patient's gender", 
                        style={'width': '55%', 'height': '100%', 'display': 'inline-block',
                          'margin': '1%', 'padding': '0','background-color': 'yellow','vertical-align': 'bottom'} # , 'font-size': '80%'
                    )
                ], style = {'width':'80%','height':'10%','margin':'2% 8% 0% 2%','background-color':'red'}),
            ],
            style={'width': '48%', 'height': '70%','margin': '2% 1%', 'background-color': 'white','display':'inline-block','vertical-align':'top'}

        ),
        # Patient Background (right)
        html.Div(
            [
                html.H3("Background Information", style={'width': '100%', 'height': '5%','margin': '0', 'background-color': 'blue','textAlign':'center'}),
                dcc.Textarea(id='background_info', style={'width': '98%', 'height': '94%','margin': '0', 'background-color': 'red'}, placeholder="Enter any background information about the patient here")
            ],
            style={'width': '48%', 'height': '70%','margin': '2% 1%', 'background-color': 'white','display':'inline-block'}
        ),

        # Other Notes (bottom)
        html.Div(
            [
                html.H3("Other notes", 
                        style={'width': '100%', 'height': '20%','margin': '0', 'background-color': 'blue','textAlign':'center'}
                ),
                dcc.Textarea(id='background_info', style={'width': '98%', 'height': '80%','margin': '0', 'background-color': 'red'}, placeholder="Enter any additional information/notes here", )
            ],
            style={'width': '95%', 'height': '16%','margin': '0% 0%','padding':'0%', 'background-color': 'white'}
        ),
    ]

    window_style = {'width': '40%', 'height': '85%', 'background-color': '#C4C4C4',
                    'position': 'fixed', 'top': '11%', 'right': '1%'}
    return (window_children, window_style)


def serve_scan_thumbnail(image_pixels, thumbnail_index, text):
    """first_frame_fig = px.imshow(image_pixels)
    first_frame_fig.update_layout(coloraxis_showscale=False)
    first_frame_fig.update_xaxes(showticklabels=False)
    first_frame_fig.update_yaxes(showticklabels=False)
    img_bytes = first_frame_fig.to_image(format="png")
    encoding = base64.b64encode(img_bytes).decode()
    img_b64 = "data:image/png;base64," + encoding """
    rgb_image_pixels = convert_color_space(image_pixels, "YBR_FULL", "RGB")
    first_frame_fig = plt.imshow(rgb_image_pixels)
    first_frame_fig.axes.get_xaxis().set_visible(False)
    first_frame_fig.axes.get_yaxis().set_visible(False)
    image_bytes = io.BytesIO()
    plt.savefig(image_bytes, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()
    img_encoding = base64.b64encode(image_bytes.getvalue()).decode()
    img_b64 = "data:image/png;base64," + img_encoding

    with open('imageInfo.txt', 'w') as f:
        f.write("name:"+text+'\n')
        f.write("shape:"+' '.join([str(value) for value in rgb_image_pixels.shape])+'\n')
        f.write("Pixel value max:" + str(np.amax(rgb_image_pixels)) + "  min:" + str(np.amin(rgb_image_pixels)) + '\n')
    with open('image.txt','w') as f:
        rgb_shape = rgb_image_pixels.shape
        rgba_image_pixels = np.empty((rgb_shape[0],rgb_shape[1],rgb_shape[2]+1))
        for i in range(0,rgb_shape[0]):
            for j in range(0,rgb_shape[1]):
                for k in range(0,rgb_shape[2]):
                    rgba_image_pixels[i,j,k] = rgb_image_pixels[i,j,k]
                rgba_image_pixels[i,j,3] = 1
        # print(rgba_image_pixels)
        # Covert to grayscale for a start
        def rgb2gray(rgb):
            r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
            gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
            return gray
        gray_image_pixels = rgb2gray(rgb_image_pixels)
        gray_first_frame_fig = plt.imshow(gray_image_pixels)
        gray_first_frame_fig.axes.get_xaxis().set_visible(False)
        gray_first_frame_fig.axes.get_yaxis().set_visible(False)
        gray_image_bytes = io.BytesIO()
        plt.savefig(gray_image_bytes, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        gray_img_encoding = base64.b64encode(gray_image_bytes.getvalue()).decode()
        f.write(gray_img_encoding)
        
    scan_thumbnail = html.Div([
        html.Button( 
            html.Img(src=img_b64, style={'width': '100%', 'height': '100%'}),
            style={'width': '100%', 'height': '90%'}, id={'type': 'scan_playbutton', 'index': thumbnail_index}
        ),
        html.H4(text,style={'margin': '0%', 'direction': 'ltr'}),
        html.Button("X",style={'width': '12%', 'height': '12%','position': 'absolute','top':'0','left':'0'}, 
                    id={'type': 'scan_remove_button', 'index': thumbnail_index})
    ], style={'witdh': '90%', 'height': '40%', 'margin': '4%','position':'relative'})

    return scan_thumbnail


def save_ds(ds_file,filename):
    # Stores the upload dicom scan (ds) in the proper filepath ()
    username = request.authorization['username']
    filepath = './Sessions/' + username + '/Dicoms/' + filename
    ds_file.save_as(filepath)


def fetch_pixelArray(filename):
    username = request.authorization['username']
    filepath = './Sessions/' + username + '/Dicoms/'+filename
    ds = pydicom.dcmread(filepath)
    return ds.pixel_array


def clear_all_dicom_files():
    # May be needed to be called with the username
    username = request.authorization['username']
    filepath = './Sessions/' + username + '/Dicoms'
    for fname in os.listdir(filepath):
        os.remove(os.path.join(filepath, fname))


# Keep this out of source code repository - save in a file or a database
valid_username_password_pairs = {
    'kon': '123',
    'kon2':'123'
}
external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__)
app.layout = serve_homepage_layout
app.config.suppress_callback_exceptions = False


auth = dash_auth.BasicAuth(
    app,
    valid_username_password_pairs
)


def handle_upload(list_of_contents, list_of_filenames, scan_thumbnails_children):
    # Since the callback's output is already in the layout, prevent_initial_call=True will not prevent the callback from being executed
    # when its input is added to the layout (the dcc.Upload element of the upload window). Thus, there is a need for a check
    if list_of_contents is None:
        raise PreventUpdate
    
    for content,filename in zip(list_of_contents, list_of_filenames):
        print('handle_upload has file: ', filename)
        content_type, content_string = content.split(',')
        
        # Firstly, verify the uploaded file is a DICOM file
        #print(content_type)

        # For every upload file, check to see whether it has been uploaded before (or is multiple times in this batch of uploads)
        """for child in scan_thumbnails_children:
            print(child[1]) """

        # Decode file bytes and read as DICOM file
        decoded_contents = base64.b64decode(content_string)
        ds = pydicom.dcmread(io.BytesIO(decoded_contents))
        # print("ds.pixel_array.shape:",ds.pixel_array.shape)
        # print("ds.Modality",ds.Modality)
        # Add scans thumbnail in th)e scans section

        thumbnail_text = filename
        # In case AcquisitionDateTime is not provided, catch the resulting error from trying to access it
        try:
            thumbnail_text = thumbnail_text + ": " + ds.AcquisitionDateTime[6:8] + "/" + ds.AcquisitionDateTime[4:6] + "/" + ds.AcquisitionDateTime[0:4] +  " " + ds.AcquisitionDateTime[8:10] + ":" + ds.AcquisitionDateTime[10:12] + ":" + ds.AcquisitionDateTime[12:14]
        except:
            thumbnail_text = thumbnail_text + ": AcquisitionDateTime Not Found"
        # In case the pixel_array is a singly image (not a video) or something else of not acceptable shape, catch that here
        if (len(ds.pixel_array.shape) == 4):
            # pixel_array is a video
            thumbnail_input =  ds.pixel_array[0, :, :, :]
        elif (len(ds.pixel_array.shape) == 3):
            # pixel_array is a single image
            thumbnail_input =  ds.pixel_array[:, :, :]
        else:
            # pixel_array is ?
            print("Error, pixel_array shape not accepted/recognized.")
            thumbnail_input = 250*np.ones((420,650,3))
        thumbnail = serve_scan_thumbnail(thumbnail_input, len(scan_thumbnails_children), thumbnail_text)
        scan_thumbnails_children.append(thumbnail)

        # Also save the file to this user's directory (server-side)
        save_ds(ds,filename)

    return scan_thumbnails_children


@app.callback(
    Output('scan_thumbnails', 'children'),
    Input({'type':'clear_all_scans_button','index':ALL},'n_clicks'),
    Input({'type': 'scan_remove_button', 'index': ALL}, 'n_clicks'),
    Input({'type': 'file_upload', 'index': ALL}, 'contents'), # pattern matching so the unrendered input won't throw an error
    State({'type': 'file_upload', 'index': ALL}, 'filename'),
    State('scan_thumbnails', 'children'),
    prevent_initial_call=True
)
def uploaded_scans_master(n_clicks_clear_scans, n_clicks_remove_scan_button, list_of_contents, list_of_filenames, scan_thumbnails_children):
    #print('\nuploaded_scans_master callback:')
    #print('prop_id of trigger:',dash.callback_context.triggered[0]['prop_id'])
    str_dict = dash.callback_context.triggered[0]['prop_id'] # stringified dict

    # If the upload_window was just closed, this callback will fire with a prop_id = '.' (why it's a dot is unknown)
    if (str_dict == '.'):
        raise PreventUpdate
    
    # So now, the callback was called either because a scan remove button was pressed, a file was uploaded or the clear scans button was pressed
    # Find the id's type
    type_value_start = str_dict.index('"type":"') + len('"type":"')
    type_value_end = str_dict.find('"}')
    type_value = str_dict[type_value_start:type_value_end]
    #print("Type of trigger:",type_value)

    # A file was uploaded
    if(type_value == 'file_upload'):
        return handle_upload(list_of_contents[0], list_of_filenames[0], scan_thumbnails_children)

    # Else, a scan_remove button was pressed
    if (type_value == 'scan_remove_button'):
         # The stringified dictionary is in the format {"index":(#remove_scan_id),"type":"scan_remove_button"}.n_clicks
        # Find the value of index (in order to know which button was clicked)
        index_value_start = str_dict.index('"index":') + len('"index":')
        index_value_end = str_dict.find(',')
        index_value = int(str_dict[index_value_start:index_value_end])
        print("Scan to be removed:",index_value)
        scan_thumbnails_children[index_value] = [] # instead of removing the thumbnail div, replace it with nothing (indexes preserved)
        return scan_thumbnails_children
    
    if (type_value == 'clear_all_scans_button'):
        print("clear_all_scans_button was pressed")
        clear_all_dicom_files()
        return []
    
    # If for some reason we've reached here, the callback trigger type was not identified
    print('uploaded_scans_master callback trigger type of',type_value,'not identified, so I am doing nothing')
    raise PreventUpdate
    

# Complex Callback that controls all button that want to output to the app's hidden div
# Some of the inputs are not initially rendered (e.g. the X button on the upload window)
# To solve this, pattern matching is once again used (see serve_scan_playback() callback)
@app.callback(
    Output('hidden_div', 'children'),
    Output('hidden_div', 'style'),
    Input({'type': 'hidden_div_button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def hidden_div_master(n_clicks):
    # This is a stringified dictionary
    str_dict = dash.callback_context.triggered[0]['prop_id']
    # The stringified dictionary is in the format {"index":"upload_button","type":"hidden_div_button"}.n_clicks
    # Find the value of index (in order to know which button was clicked)
    index_value_start = str_dict.index('"index":"') + len('"index":"')
    index_value_end = str_dict.find('",')
    index_value = str_dict[index_value_start:index_value_end]

    # Here, depending on the button clicked, are the children that will be on hidden_div
    new_window_children = []
    new_window_style = {}  # style preset to the underlying hidden div

    if (index_value == 'upload_button'):
        # The upload ECHO Scan button is clicked, so serve the upload layout to the user
        new_window_children = serve_upload_layout()
        new_window_style = {'width': '40%', 'height': '40%',
                            'background-color': 'white', 'position': 'fixed', 'top': '20%', 'left': '30%'}

    if (index_value == 'upload_window_X_button'):
        # The X button on the upload layout has been clicked, so erase the children of the div and make it hidden again
        # If any files were uploaded?
        new_window_children = []
        new_window_style = {'z-index': '-1'}

    if (index_value == 'patient_info_button'):
        (new_window_children, new_window_style) = serve_patient_info_form()

    return (new_window_children, new_window_style)


@app.callback(
    Output('scan_playback_section', 'children'),
    Input({'type': 'scan_playbutton', 'index': ALL}, 'n_clicks'),
    State('scan_thumbnails', 'children'),
    prevent_initial_call=True
)
def serve_scan_playback(n_clicks, scan_thumbnails_children):
    # Right now this fires every time a scan thumbnail is added, so a check is implemented to stop the scan playback selected from changing every such time. When a click occurs, the length of the triggers is 1 (just the button that was clicked), whereas when the thumbnail area is updated, the length of the triggers is the new number of thumbnails in the thumbnail area. The end case being that this callback executes for every thumbnail button clicked, when there are two thumbnails and one is removed (leaving only one in the thumbnail area) or when the first thumbnail is added.
    #print("thumbnails:",len(scan_thumbnails_children))
    if (len(dash.callback_context.triggered) > 1):
        raise PreventUpdate

    # This is a stringified dictionary
    str_dict = dash.callback_context.triggered[0]['prop_id']
    scan_index_str = ""
    # The only number in that stringified dictionary is the index of the 'scan_playbutton' triggered
    for letter in str_dict:
        if letter.isdigit():
            scan_index_str = scan_index_str + letter
    # In case all scans were deleted, the below code will throw an error, catch it
    try:
        scan_index = int(scan_index_str)
    except:
        scan_index = -1
    if (scan_index == -1): 
        raise PreventUpdate

    # Get the current DICOM filename the scan_index belongs to
    thumbnail_text = scan_thumbnails_children[scan_index]['props']['children'][1]['props']['children']
    filename = thumbnail_text.split(":")[0]
    pixel_array = fetch_pixelArray(filename)

    # Convert pixelArray to a list of flattened 3-D arrays
    def rgb2rgba(rgb,A):
        # Transforms an RGB picture into an RGBA one (adds A channel)
        rows,cols,ch = rgb.shape
        rgba = A*np.ones(shape=(rows,cols,4))
        for i in range(0,rows):
            for j in range(0,cols):
                for k in range(0,4):
                    if (k==3): continue
                    rgba[i,j,k] = rgb[i,j,k]
        return rgba
    
    rgb = convert_color_space(pixel_array, "YBR_FULL", "RGB") # proper RGB presentation
    image_pixels_list = list()
    for i in range(0,rgb.shape[0]):
        rgbPic = rgb[i,:,:,:]
        rgbaPic = rgb2rgba(rgbPic,255)
        flat_rgbaPic = rgbaPic.flatten(order='C')
        image_pixels_list.append(flat_rgbaPic)
    
    return cvp.cornerstoneVP(
            id='CVP',
            imagePixelsList = image_pixels_list,
            imageId = 0,
            imageIds = range(0,rgb.shape[0])
    )




@app.callback(
    Output(component_id='scan_count', component_property='children'),
    Input(component_id='scan_thumbnails', component_property='children')
)
def update_scan_count(scan_count_children):
    # Get the number of dicom files this user has uploaded
    username = request.authorization['username']
    filepath = './Sessions/' + username + '/Dicoms/'
    scan_number = len(os.listdir(filepath))
    info = "Scan Count: " + str(scan_number)
    return info


@app.callback(
    Output(component_id='date_time', component_property='children'),
    Input(component_id='interval_component', component_property='n_intervals')
)
def update_datetime(n_intervals):
    return serve_datetime()


if __name__ == '__main__':
    app.run_server(debug=True)