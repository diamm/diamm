/*
 * Retrieves iiif data from structures block
 */
window.divaPlugins.push((function ()
{
    var item_div = $("#image-item-listing");
    var structures = [];
    var items = [];

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
        };
    }

    var populateStructures = function (manifest)
    {
        var displayItem = function (item) 
        {
            item_div.append("<p><strong>Composers: </strong>" + item[0].composers[0].name + "</p>");
        };

        var cacheAndDisplayItem = function (serviceId)
        {
            return function (item)
            {
                items[serviceId] = item;
                displayItem (item);
            };

        };

        var fetchItems = function (services) 
        {
            for (var i = 0, slen = services.length; i < slen; i++)
            {
                item_div.append("<h3>" + services[i].label + "</h3>");
                if (items[services[i].id])
                {
                    displayItem(items[services[i].id]);
                } else
                {
                    $.ajax({
                        dataType: "json",
                        url: services[i].id,
                        success: cacheAndDisplayItem (services[i].id)
                    });
                }
            }
        };

        var displayItems = function (pageIndex, filename)
        {
            //Clear the item div
            item_div.empty().append("<h2>" + filename + "</h2>");

            var services = structures[filename];
            if (services)
            {
                fetchItems (services);
            }
        };

        var getStructures = function (manifestStructures)
        {
            for (var i=0, slen = manifestStructures.length; i < slen; i++)
            {
                var members = manifestStructures[i].members;
                for (var j=0, mlen = members.length; j < mlen; j++)
                {
                    var canvasID = members[j].label;
                    if (structures[canvasID] === undefined)
                    {
                        structures[canvasID] = [];
                    }
                    structures[canvasID].push({
                        label: manifestStructures[i].label,
                        id: manifestStructures[i].service['@id']
                    });
                }
            }
        };

        getStructures(manifest.structures);
        displayItems(null, manifest.sequences[0].canvases[0].label);
        diva.Events.subscribe('VisiblePageDidChange', debounce(displayItems, 100));
    };


    return {
        pluginName: 'IIIFStructure',
        init: function(settings)
        {
            console.log('Initializing IIIFStructure plugin');
            diva.Events.subscribe('ManifestDidLoad', populateStructures);
        }
    };
})());
