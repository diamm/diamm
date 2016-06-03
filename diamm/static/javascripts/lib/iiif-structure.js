/*
 * Retrieves iiif data from structures block
 */
window.divaPlugins.push((function ()
{
    var canvasServices = [];

    // Adapted from Underscore.js
    // Returns a function that will only be trigerred 'wait' milliseconds
    // after the last time it was called.
    // the function will be triggered on the leading edge instead of trailing
    function debounce (func, wait)
    {
        var timeout;
        return function()
        {
            var context = this, args = arguments;
            var later = function()
            {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        }
    }

    var populateCanvasServices = function (manifest)
    {
        var getService = function (pageIndex, filename)
        {
            var serviceID = canvasServices[filename];
            $.ajax({
                url: serviceID,
                success: function (data) { console.log(serviceID); console.log(filename); }
            });
        };

        var getCanvasServices = function (structures)
        {
            for (var i=0, slen = structures.length; i < slen; i++)
            {
                var members = structures[i].members;
                for (var j=0, mlen = members.length; j < mlen; j++)
                {
                    var canvasID = members[j].label;
                    if (canvasServices[canvasID] === undefined)
                    {
                        canvasServices[canvasID] = [];
                    }
                    canvasServices[canvasID].push(structures[i].service['@id']);
                }
            }
            console.log(canvasServices);
        };

        getCanvasServices(manifest.structures);
        diva.Events.subscribe('VisiblePageDidChange', debounce(getService, 250));
    };


    return {
        pluginName: 'IIIFStructure',
        init: function(settings)
        {
            console.log('Initializing IIIFStructure plugin');
            diva.Events.subscribe('ManifestDidLoad', populateCanvasServices);
        }
    };
})());
