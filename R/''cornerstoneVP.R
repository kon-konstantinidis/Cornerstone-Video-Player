# AUTO GENERATED FILE - DO NOT EDIT

#' @export
''cornerstoneVP <- function(id=NULL, dicomDateTime=NULL, dicomName=NULL, framerate=NULL, imageHeight=NULL, imagePixelsList=NULL, imageWidth=NULL) {
    
    props <- list(id=id, dicomDateTime=dicomDateTime, dicomName=dicomName, framerate=framerate, imageHeight=imageHeight, imagePixelsList=imagePixelsList, imageWidth=imageWidth)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'cornerstoneVP',
        namespace = 'cvp',
        propNames = c('id', 'dicomDateTime', 'dicomName', 'framerate', 'imageHeight', 'imagePixelsList', 'imageWidth'),
        package = 'cvp'
        )

    structure(component, class = c('dash_component', 'list'))
}
