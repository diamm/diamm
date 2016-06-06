/*
 * Retrieves iiif data from structures block
 */
window.divaPlugins.push((function ()
{
    var structures = [];
    var items = [];

    var item_div = document.getElementById("image-item-listing");
    var addVisibilityToggle = function (div)
    {
        div.style.display = 'none';
        function toggleVisibility ()
        {
            if (div.style.display === 'block')
            {
                div.style.display = 'none';
            }
            else
            {
                div.style.display = 'block';
            }
        }

        console.log(div);
        div.parentElement.onclick = toggleVisibility;
    };

    // Adapted from Underscore.js
    // Returns a function that will only be trigerred 'wait' milliseconds
    // after the last time it was called.
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
            var para = document.createElement("P");
            var t = document.createTextNode("Composers: " + item[0].composers[0].name);
            para.appendChild(t);
            item_div.appendChild(para);
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
                var h3 = document.createElement("H3");
                var t = document.createTextNode(services[i].label);
                h3.appendChild(t);
                item_div.appendChild(h3);

                if (items[services[i].id])
                {
                    displayItem(items[services[i].id]);
                }
                else
                {
                    $.ajax({
                        dataType: "json",
                        url: services[i].id,
                        success: cacheAndDisplayItem(services[i].id)
                    });
                }
            }
        };

        var displayItems = function (pageIndex, filename)
        {
            //Clear the item div
            while (item_div.firstChild)
            {
                item_div.removeChild(item_div.firstChild);
            }

            var h2 = document.createElement("H2");
            var t = document.createTextNode(filename);
            h2.appendChild(t);
            item_div.appendChild(h2);
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
