
module Cvp
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("jl/''_cornerstonevp.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "cvp",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "async-cornerstoneVP.js",
    external_url = "https://unpkg.com/cvp@0.0.1/cvp/async-cornerstoneVP.js",
    dynamic = nothing,
    async = :true,
    type = :js
),
DashBase.Resource(
    relative_package_path = "async-cornerstoneVP.js.map",
    external_url = "https://unpkg.com/cvp@0.0.1/cvp/async-cornerstoneVP.js.map",
    dynamic = true,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "cvp.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "cvp.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
