/*
 * Retrieves iiif data from structures block
 */
window.divaPlugins.push((function ()
{
    var structures = [];
    var items = [];

    var itemsDiv = document.getElementById("image-item-listing");
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

        div.parentElement.onclick = toggleVisibility;
        div.parentElement.style.cursor = 'pointer';
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
        var displayItem = function (item, serviceLabel)
        {
            console.log(serviceLabel);
            console.log(item);
            console.log(item[0].composers[0].name);
            var itemDiv = document.createElement("DIV");
            var H3 = document.createElement("h3"); 
            var t = document.createTextNode(serviceLabel);
            H3.appendChild(t);
            var itemDetailsDiv = document.createElement("DIV");
            var para = document.createElement("P");
            var text = "";
            for (var i = 0, clen = item[0].composers.length; i < clen; i++)
            {
                text += item[0].composers[i].name + " ";
            }
            t = document.createTextNode("Composer: " + text);
            para.appendChild(t);
            itemDetailsDiv.appendChild(para);
            itemDiv.appendChild(H3);
            itemDiv.appendChild(itemDetailsDiv);
            itemsDiv.appendChild(itemDiv);
        };

        var cacheAndDisplayItem = function (service)
        {
            return function (item)
            {
                items[service.id] = item;
                displayItem (item, service.label);
            };

        };

        var fetchItems = function (services)
        {
            for (var i = 0, slen = services.length; i < slen; i++)
            {
                var service = services[i];
                if (items[service.id])
                {
                    displayItem(items[service.id], service.label);
                }
                else
                {
                    $.ajax({
                        dataType: "json",
                        url: service.id,
                        success: cacheAndDisplayItem(service)
                    });
                }
            }
        };

        var displayItems = function (pageIndex, filename)
        {
            //Clear the item div
            while (itemsDiv.firstChild)
            {
                itemsDiv.removeChild(itemsDiv.firstChild);
            }

            var h2 = document.createElement("H2");
            var t = document.createTextNode(filename);
            h2.appendChild(t);
            itemsDiv.appendChild(h2);
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
