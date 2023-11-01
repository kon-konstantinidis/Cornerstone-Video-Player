% Auto-generated: do not edit by hand
\name{''cornerstoneVP}

\alias{''cornerstoneVP}

\title{cornerstoneVP component}

\description{
CornerstoneVP is the custom cornerstone  dicom video player component, made for Dash. It takes a list of images and displays them, whilst giving additional controls and mouse  tools to the user, per the cornerstone library.
}

\usage{
''cornerstoneVP(id=NULL, dicomDateTime=NULL, dicomName=NULL, framerate=NULL,
imageHeight=NULL, imagePixelsList=NULL, imageWidth=NULL)
}

\arguments{


\item{id}{Character. The ID used to identify this component in Dash callbacks.}

\item{dicomDateTime}{Character. The date-time of the video to be displayed}

\item{dicomName}{Character. The DICOM filename of the video to be displayed}

\item{framerate}{Numeric. Initially set framerate}

\item{imageHeight}{Numeric. The height of the images in the imagePixelsList}

\item{imagePixelsList}{List of list of numericss. A list of the image pixel 1D data array of all images}

\item{imageWidth}{Numeric. The width of the images in the imagePixelsList}
}

\value{named list of JSON elements corresponding to React.js properties and their values}

