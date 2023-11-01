import React, { Component } from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import * as cornerstone from 'cornerstone-core';
import * as cornerstoneTools from 'cornerstone-tools';
import * as cornerstoneMath from 'cornerstone-math';

/**
 * CornerstoneVP is the custom cornerstone 
 * dicom video player component, made for Dash.
 * It takes a list of images and displays them,
 * whilst giving additional controls and mouse 
 * tools to the user, per the cornerstone library.
 */
export default class CornerstoneVP extends Component {

    /**
    * Custom image loader to register with cornerstone
    * The imageId_data should be in format:
    * dicomImageLoader://{imageId}_{imageHeight}-{imageWidth}_{imagePixelData}
    */
    getDicomImage(imageId_data) {
        //console.log("\n---------- getDicomImage ----------");
        //console.log("getDicomImage called with imageId_data: ",imageId_data);

        function getIndicesOf(searchStr, str) {
            var searchStrLen = searchStr.length;
            if (searchStrLen == 0) {
                return [];
            }
            var startIndex = 0, index, indices = [];
            while ((index = str.indexOf(searchStr, startIndex)) > -1) {
                indices.push(index);
                startIndex = index + searchStrLen;
            }
            return indices;
        }
        var underscore_indices = getIndicesOf("_", imageId_data);
        //console.log("_ locations at: ", underscore_indices)

        let imageIndex = imageId_data.substring("dicomImageLoader://".length, underscore_indices[0]);
        //console.log("getDicomImage loading image with index: ",imageIndex);

        let imageDims = imageId_data.substring(underscore_indices[0] + 1, underscore_indices[1]);
        const height = Number(imageDims.substring(0, imageDims.search("-")));
        const width = Number(imageDims.substring(imageDims.search("-") + 1, imageDims.length));
        //console.log("getDicomImage loading image with height", height, "and width", width);

        let pixelData = imageId_data.substring(underscore_indices[1] + 1, imageId_data.length);
        pixelData = pixelData.split(",") // string array of numbers
        pixelData = pixelData.map(Number) // convert strings to numbers
        //console.log("pixelData:\n",typeof(pixelData));
        //console.log("getDicomImage loading image with pixelData", pixelData);

        function getPixelData() {
            return pixelData;
        }

        var image = {
            imageId: imageIndex,
            minPixelValue: 0,
            maxPixelValue: 255,
            slope: 1.0,
            intercept: 0,
            windowCenter: height / 2,
            windowWidth: width,
            render: cornerstone.renderColorImage,
            getPixelData: getPixelData,
            //getImageData: getImageData,
            //getCanvas: getCanvas,
            rows: height,
            columns: width,
            height: height,
            width: width,
            color: true,
            rgba: true,
            columnPixelSpacing: 1,
            rowPixelSpacing: 1,
            invert: false,
            sizeInBytes: width * height * 4
        };
        return {
            promise: new Promise((resolve) => {
                resolve(image);
            }),
            cancelFn: function () { console.log("cancelFn"); }
        };
    }

    constructor(props) {
        console.log("constructor");
        super(props);
        cornerstoneTools.external.cornerstone = cornerstone;
        cornerstoneTools.external.cornerstoneMath = cornerstoneMath;
        //console.log("CVP: cornerstoneTools initialized.");

        // Register local custom image loader with cornerstone 
        cornerstone.registerImageLoader("dicomImageLoader", this.getDicomImage);
        //console.log("Image Loader registered");

        this.state = {
            dicomName: "",
            dicomDateTime:"",
            framerate:0, //initiallized so the slider input is a controllable component
            playButtonId: this.props.id.concat("_playButton"),
            stopButtonId: this.props.id.concat("_stopButton"),
            previousFrameButtonId: this.props.id.concat("_previousFrame"),
            nextFrameButtonId: this.props.id.concat("_nextFrame"),
            framerateSliderId: this.props.id.concat("_framerateSlider"),
            framerateDisplayId: this.props.id.concat("_framerateDisplay")
        };
    }


    static getDerivedStateFromProps(nextProps,prevState){
        console.log("getDerivedStateFromProps");
        console.log("prevState:",prevState);
        console.log("nextProps:",nextProps);
        if (nextProps.imagePixelsList!== undefined && nextProps.imagePixelsList.length>0 && nextProps.dicomName !== prevState.dicomName){
            console.log("getDerivedStateFromProps doing work.");
            // Produce imageIDs_data for the image pixel list
            const numOfImages = nextProps.imagePixelsList.length;
            var imageIDs = new Array();
            var imageIDs_data = new Array();
            for (var i = 0; i < numOfImages; i++) {
                var id = "dicomImageLoader://".concat(i);
                imageIDs.push(id);
                // Add dimensions
                id = id.concat("_", nextProps.imageHeight, "-", nextProps.imageWidth)
                id = id.concat("_", nextProps.imagePixelsList[i]);
                imageIDs_data.push(id);
            }
            //console.log(imageIDs);
            prevState.imageIDs = imageIDs;
            prevState.imageIDs_data = imageIDs_data;
            prevState.dicomName = nextProps.dicomName;
            prevState.dicomDateTime = nextProps.dicomDateTime;
            prevState.imageHeight = nextProps.imageHeight;
            prevState.imageWidth = nextProps.imageWidth;
            prevState.framerate = nextProps.framerate;
            /*
            const newState = {
                imageIDs: imageIDs,
                imageIDs_data: imageIDs_data,
                dicomName: nextProps.dicomName,
                dicomDateTime: nextProps.dicomDateTime,
                imageHeight: nextProps.imageHeight,
                imageWidth: nextProps.imageWidth,
                framerate: nextProps.framerate
            };
            */
            return prevState;
        }
        return null;
    }

    shouldComponentUpdate(nextProps, nextState){
        console.log("shouldComponentUpdate");
        console.log("this.state:",this.state);
        console.log("nextProps:",nextProps);
        /*
        if (nextProps.imagePixelsList == undefined || nextProps.imagePixelsList.length == 0 || nextProps.dicomName == undefined) {
            console.log("false");
            return false;
        }
        */
        if (nextProps.dicomName == undefined) {
            console.log("false");
            return false;
        }
        console.log("true");
        return true;
    }

    // Arrow functions used so access to the component's "this" keyword is provided
    onPlayButtonClick = () =>{
        //console.log("onPlayButtonClick");
        if (this !== undefined && this.element !== undefined && this.state.framerate !== undefined){
            cornerstoneTools.playClip(this.element,this.state.framerate)
        }
    }
    onStopButtonClick = () =>{
        //console.log("onStopButtonClick");
        if (this !== undefined && this.element !== undefined){
            cornerstoneTools.stopClip(this.element)
        }
    }
    onPreviousFrameButtonClick = () =>{
        //console.log("onPreviousFrameButtonClick");
        const element = this.element;
        var stackState = cornerstoneTools.getToolState(element, 'stack');
        if (stackState !== undefined){
            let currentFrameImageIndex = stackState.data[0].currentImageIdIndex;
            let numberOfFrames = stackState.data[0].imageIds.length;
            let newFrameIndex = (currentFrameImageIndex - 1) % numberOfFrames;
    
            // Display the previous frame
            cornerstone.loadImage(stackState.data[0].imageIds[newFrameIndex]).then(function (image) {
                cornerstone.displayImage(element, image);
            });
    
            // Update stack so the playClip assumes from this frame
            // Define the stack object
            var stack = {
                currentImageIdIndex: newFrameIndex,
                imageIds: stackState.data[0].imageIds
            };
            cornerstoneTools.clearToolState(element,'stack');
            cornerstoneTools.addToolState(element, 'stack', stack);
        }
    }
    onNextFrameButtonClick = () =>{
        //console.log("onNextFrameButtonClick");
        const element = this.element;
        var stackState = cornerstoneTools.getToolState(element, 'stack');
        if (stackState !== undefined){
            let currentFrameImageIndex = stackState.data[0].currentImageIdIndex;
            let numberOfFrames = stackState.data[0].imageIds.length;
            let newFrameIndex = (currentFrameImageIndex + 1) % numberOfFrames;
    
            // Display the next frame
            cornerstone.loadImage(stackState.data[0].imageIds[newFrameIndex]).then(function (image) {
                cornerstone.displayImage(element, image);
            });
    
            // Update stack so the playClip assumes from this frame
            // Define the stack object
            var stack = {
                currentImageIdIndex: newFrameIndex,
                imageIds: stackState.data[0].imageIds
            };
            cornerstoneTools.clearToolState(element,'stack');
            cornerstoneTools.addToolState(element, 'stack', stack);
        }
    }
    onSliderChange = (event) => {
        //console.log("onSliderChange");
        //console.log("this:",this);
        //console.log("event:",event);
        //console.log("cornerstoneTools.getToolState(this.element, 'stack'):",cornerstoneTools.getToolState(this.element, 'stack'));

        if (this !== undefined && this.element !== undefined && cornerstoneTools.getToolState(this.element, 'stack') !== undefined){
            /*
            setState here won't triger an update because the dicomName field of the state remains the same
            render() does not execute so we change the framerate display values by hand (lighter)
            It will however update the state with the new framerate (so onPlayButtonClick has access to it)
            */
            this.setState({framerate:event.target.value});
            document.getElementById(this.state.framerateSliderId).value = event.target.value;
            document.getElementById(this.state.framerateDisplayId).innerHTML = "Framerate: " + event.target.value;
            cornerstoneTools.playClip(this.element, event.target.value); //let the user resume the playback after stopping it?
        }
    }

    render() {
        console.log("rendering");
        return (
            <div style={{ width: "100%", height: "100%", backgroundColor: "black" }}>
                <div
                    style={{ width: "100%", height: "95%" }}
                    className={classNames('viewport-wrapper')}
                >
                    <div
                        style={{ width: "100%", height: "100%" }}
                        className="viewport-element"
                        onContextMenu={(e) => e.preventDefault()}
                        onMouseDown={(e) => e.preventDefault()}
                        ref={(input) => {
                            this.element = input;
                        }}
                    >
                        {
                            /* This classname is important in that it tells `cornerstone` to not
                            * create a new canvas element when we "enable" the `viewport-element`
                            */
                        }
                        <canvas className="cornerstone-canvas" />
                    </div>
                </div>
                {
                    /*
                    * margin:'top right bottom left'
                    */
                }
                <div className={"playback-controls"} style={{ width: "100%", height: "5%", verticalAlign: 'middle' }}>
                    <p style={{ width: '10%', height: '100%', margin: '0% 0% 0% 1%', display: 'inline-block', verticalAlign: 'middle', color: "yellow", textAlign: "left" }}>{this.state.dicomName}</p>
                    <button id={this.state.playButtonId} onClick={this.onPlayButtonClick}
                        style={{ width: '5%', height: '100%', margin: '0% 0% 0% 12%', verticalAlign: 'middle' }}>Play
                    </button>
                    <button id={this.state.stopButtonId} onClick={this.onStopButtonClick}
                        style={{ width: '5%', height: '100%', margin: '0% 0% 0% 1%', verticalAlign: 'middle' }}>Stop
                    </button>
                    <button id={this.state.previousFrameButtonId} onClick={this.onPreviousFrameButtonClick}
                        style={{ width: '12%', height: '100%', margin: '0% 0% 0% 1%', verticalAlign: 'middle' }}>Previous Frame
                    </button>
                    <button id={this.state.nextFrameButtonId} onClick={this.onNextFrameButtonClick}
                        style={{ width: '12%', height: '100%', margin: '0% 0% 0% 1%', verticalAlign: 'middle' }}>Next Frame
                    </button>
                    {/*
                    defaultValue used in input of type range instead of value, because using value arises
                    the need to re-render every time the framerate slider changes, that's slow
                    Instead, the value is initialized once as {this.state.framerate} and then it's updated
                    by the onChange handler, without re-rendering the component
                    */}
                    <input type="range" min="1" max="120" defaultValue={this.state.framerate} onChange={this.onSliderChange} 
                    id={this.state.framerateSliderId}
                    style={{ width: '12%', height: '100%', margin: '0% 0% 0% 3%', verticalAlign: 'middle' }}>
                    </input>
                    <p id={this.state.framerateDisplayId}
                        style={{ width: '13%', height: '100%', margin: '0% 0% 0% 1%', display: 'inline-block', verticalAlign: 'middle', color: "yellow", textAlign: "center" }}>
                            Framerate: {this.state.framerate}
                    </p>
                    {/* Redudant, date is already visible from the app's sidebar
                    <p style={{ width: '18%', height: '100%', margin: '0% 1% 0% 3%', display: 'inline-block', verticalAlign: 'middle', color: "yellow", textAlign: "right" }}>{this.state.dicomDateTime}</p>
                    */}
                </div>
            </div>
        );
    }

    componentDidMount() {
        console.log("CVP: Mounting.");
        const element = this.element;

        // Enable the DOM Element for use with Cornerstone
        cornerstone.enable(this.element);

        // Add mouse tools
        cornerstoneTools.mouseInput.enable(this.element);
        cornerstoneTools.wwwc.activate(this.element, 1); // ww/wc is the default tool for left mouse button
        cornerstoneTools.pan.activate(this.element, 2); // pan is the default tool for middle mouse button
        cornerstoneTools.zoom.activate(this.element, 4); // zoom is the default tool for right mouse button

        
        if (this.state.imageIDs_data == undefined){
            // If the CVP was called with no video to display, stop here
            document.getElementById(this.state.framerateSliderId).disabled = true; 
            document.getElementById(this.state.framerateDisplayId).innerHTML = "Framerate: "; 
            console.log("CVP initiallized with no video");
            return;
        }
   
        // Display the first frame of the video
        cornerstone.loadImage(this.state.imageIDs_data[0]).then(function (image) {
            cornerstone.displayImage(element, image);
        });

        // Define the stack object
        var stack = {
            currentImageIdIndex: 0,
            imageIds: this.state.imageIDs_data
        };

        // Add stack/playback tools
        cornerstoneTools.clearToolState(this.element, 'stack');
        cornerstoneTools.addStackStateManager(this.element, [
            'stack',
            'playClip',
        ]);
        cornerstoneTools.addToolState(this.element, 'stack', stack);
        cornerstoneTools.playClip(this.element, this.state.framerate);

        // Set proper framerate and framerate slider value (so no need for re-render)
        document.getElementById(this.state.framerateDisplayId).innerHTML = "Framerate: " + this.state.framerate;
        document.getElementById(this.state.framerateSliderId).value = this.state.framerate;
        console.log("CVP: Mounted.");
    }

    componentDidUpdate(prevProps,prevState){
        console.log("componentDidUpdate");
        console.log("this.props:",this.props);
        console.log("prevProps:",prevProps);
        if (this.props.dicomName !== prevProps.dicomName && this.props.imagePixelsList.length > 0 ) {
            console.log("componentDidUpdate doing work.");
            
            // Stop previous video and clear the stack and playclip tools
            cornerstoneTools.stopClip(this.element);
            cornerstoneTools.clearToolState(this.element, 'stack');
            cornerstoneTools.clearToolState(this.element, 'playclip');

            // If the CVP was initiallized empty, this slider was disabled, so enable it now
            if (document.getElementById(this.state.framerateSliderId).disabled == true){
                document.getElementById(this.state.framerateSliderId).disabled = false;
            }

            // Display the new video's starting image
            const element = this.element;
            cornerstone.loadImage(this.state.imageIDs_data[0]).then(function (image) {
                cornerstone.displayImage(element, image);
            });

            // Define the new stack object
            var stack = {
                currentImageIdIndex: 0,
                imageIds: this.state.imageIDs_data
            };

            // Add stack/playback
            cornerstoneTools.addStackStateManager(this.element, [
                'stack',
                'playClip',
            ]);
            cornerstoneTools.addToolState(this.element, 'stack', stack);
            cornerstoneTools.playClip(this.element, this.state.framerate);

            // Set proper framerate and framerate slider value (so no need for re-render)
            document.getElementById(this.state.framerateDisplayId).innerHTML = "Framerate: " + this.state.framerate;
            document.getElementById(this.state.framerateSliderId).value = this.state.framerate;
        }
    }
    
    componentWillUnmount() {
        console.log("CVP unmounting.");
        cornerstoneTools.stopClip(this.element);
        cornerstoneTools.clearToolState(this.element);
        cornerstone.disable(this.element);
        console.log("CVP unmounted");
    }
}

CornerstoneVP.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string.isRequired,

    /**
    * A list of the image pixel 1D data array of all images
    */
    imagePixelsList: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.number)),

    /**
     * The DICOM filename of the video to be displayed 
     */
    dicomName: PropTypes.string,

    /**
     * The date-time of the video to be displayed
     */
    dicomDateTime: PropTypes.string,

    /**
     * The height of the images in the imagePixelsList
     */
    imageHeight: PropTypes.number,

    /**
     * The width of the images in the imagePixelsList
     */
    imageWidth: PropTypes.number,

    /**
     * Initially set framerate
     */
    framerate: PropTypes.number
};

CornerstoneVP.defaultProps = {
    imagePixelsList: undefined,
    dicomName: undefined,
    dicomDateTime: undefined,
    imageHeight: undefined,
    imageWidth: undefined,
    framerate: undefined
};

export const defaultProps = CornerstoneVP.defaultProps;
export const propTypes = CornerstoneVP.propTypes;


