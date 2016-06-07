/*
 * Retrieves iiif data from structures block
 */
window.divaPlugins.push((function ()
{
    var structures = [];
    var items = [];

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

    var itemsDiv = document.getElementById("image-item-listing");
    var addVisibilityToggle = function (element)
    {
        element.style.display = 'none';
        function toggleVisibility ()
        {
            if (element.style.display === 'block')
            {
                element.style.display = 'none';
            }
            else
            {
                element.style.display = 'block';
            }
        }

        element.parentElement.onclick = toggleVisibility;
        element.parentElement.style.cursor = 'pointer';
    };

    var populateStructures = function (manifest)
    {
        function getCompositionItem (composition)
        {
            var li, t, a;
            li = document.createElement("li");
            t = document.createTextNode("Composition: ");
            li.appendChild(t);
            a = document.createElement("a");
            t = document.createTextNode(composition.title);
            a.setAttribute('href', composition['@id']);
            a.appendChild(t);
            li.appendChild(a);

            return li;
        }

        function getComposersItem (composers)
        {
            var li, t, a;
            li = document.createElement("li");
            t = document.createTextNode("Composer: ");
            li.appendChild(t);
            for (var i = 0, clen = composers.length; i < clen; i++)
            {
                if (composers[i]['@id'])
                {
                    a = document.createElement("a");
                    t = document.createTextNode(composers[i].name + " ");
                    a.setAttribute('href', composers[i]['@id']);
                    a.appendChild(t);
                    li.appendChild(a);
                }
                else
                {
                    t = document.createTextNode(composers[i].name + " ");
                    li.appendChild(t);
                }

                if (composers[i].uncertain)
                {
                    t = document.createTextNode("? ");
                    li.appendChild(t);
                }
            }

            return li;
        }

        function getFolioItem (folio)
        {
            var li;
            li = document.createElement("li");
            if (folio.start.label === folio.end.label)
            {
                t = document.createTextNode("Folio: " + folio.start.label);
            }
            else
            {
                t = document.createTextNode("Folio: " + folio.start.label + "-" + folio.end.label);

            }
            li.appendChild(t);
            return li;
        }

        function getVoicesItem (voices)
        {
            var ul, ul2, li, li2, div, t;
            li = document.createElement("li");
            t = document.createTextNode("Voices");
            div = document.createElement("div");
            div.appendChild(t);
            li.appendChild(div);

            for (i = 0, vlen = voices.length; i < vlen; i++)
            {
                ul = document.createElement("ul");
                t = document.createTextNode(voices[i].voice_text);
                li2 = document.createElement("li");
                li2.appendChild(t);
                ul.appendChild(li2);

                ul2 = document.createElement("ul");
                if (voices[i].voice_type !== "no designation")
                {
                    t = document.createTextNode("Type: " + voices[i].voice_type);
                    li2 = document.createElement("li");
                    li2.appendChild(t);
                    ul2.appendChild(li2);
                }

                li2 = document.createElement("li");
                t = document.createTextNode("Language: " + voices[i].languages[0]);
                li2.appendChild(t);
                ul2.appendChild(li2);
                ul.appendChild(ul2);
            }

            div.appendChild(ul);
            addVisibilityToggle(ul);
            li.appendChild(div);
            return li;
        }

        var displayItem = function (item, serviceLabel)
        {
            var itemDiv, itemDetailsDiv, h3, t, ul, li;
            itemDiv = document.createElement("div");
            h3 = document.createElement("h3");
            t = document.createTextNode(serviceLabel);
            h3.appendChild(t);
            itemDetailsDiv = document.createElement("div");
            ul = document.createElement("ul");

            // composition
            li = getCompositionItem(item[0].composition);
            ul.appendChild(li);

            // composer
            li = getComposersItem(item[0].composers);
            ul.appendChild(li);

            // folio
            li = getFolioItem (item[0].folios);
            ul.appendChild(li);

            // voices
            li = getVoicesItem(item[0].voices);
            ul.appendChild(li);

            itemDiv.appendChild(h3);
            itemDetailsDiv.appendChild(ul);
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

            var h2 = document.createElement("h2");
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
