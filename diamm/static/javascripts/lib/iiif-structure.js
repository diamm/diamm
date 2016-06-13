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
    function addVoiceVisibilityToggle (element)
    {
        var button = element.parentElement.firstChild; 
        element.style.display = 'none';

        var toggleVisibility = function ()
        {
            if (element.style.display === 'block')
            {
                button.lastChild.remove();
                i = document.createElement("i");
                i.setAttribute("class", "fa fa-caret-down");
                button.appendChild(i);
                element.style.display = 'none';
            }
            else
            {
                button.lastChild.remove();
                i = document.createElement("i");
                i.setAttribute("class", "fa fa-caret-up");
                button.appendChild(i);
                element.style.display = 'block';
            }
        };
        button.onclick = toggleVisibility;
        button.style.cursor = 'pointer';
    }

    var populateStructures = function (manifest)
    {
        function getCompositionAnchor (composition)
        {
            var t, a;
            a = document.createElement("a");
            t = document.createTextNode(composition.title);
            a.setAttribute('href', composition['@id']);
            a.appendChild(t);

            return a;
        }

        function getComposersPara (composers)
        {
            var p, t, a;
            p = document.createElement("p");
            t = document.createTextNode("Composer: ");
            strong = document.createElement("strong");
            strong.appendChild(t);
            p.appendChild(strong);
            for (var i = 0, clen = composers.length; i < clen; i++)
            {
                if (composers[i]['@id'])
                {
                    a = document.createElement("a");
                    t = document.createTextNode(composers[i].name + " ");
                    a.setAttribute('href', composers[i]['@id']);
                    a.appendChild(t);
                    p.appendChild(a);
                }
                else
                {
                    t = document.createTextNode(composers[i].name + " ");
                    p.appendChild(t);
                }

                if (composers[i].uncertain)
                {
                    t = document.createTextNode("? ");
                    p.appendChild(t);
                }
            }

            return p;
        }

        function getVoicesPara (voices)
        {
            var p, t, i;
            p = document.createElement("p");
            strong = document.createElement("strong");
            t = document.createTextNode("Voices ");
            strong.appendChild(t);
            i = document.createElement("i");
            i.setAttribute("class", "fa fa-caret-down");
            strong.appendChild(i);
            p.appendChild(strong);

            for (i = 0, vlen = voices.length; i < vlen; i++)
            {
                p2 = document.createElement("p");
                p2.style.textIndent = '-1em';
                p2.style.marginLeft = '1em';
                t = document.createTextNode("Incipit: " + voices[i].voice_text);
                p2.appendChild(t);

                var ul = document.createElement("ul");
                t = document.createTextNode("Type: " + voices[i].voice_type);
                var li = document.createElement("li");
                li.appendChild(t);
                ul.appendChild(li);

                t = document.createTextNode("Language: " + voices[i].languages[0]);
                li = document.createElement("li");
                li.appendChild(t);
                ul.appendChild(li);

                p2.appendChild(ul);
                p.appendChild(p2);
                addVoiceVisibilityToggle(p2);
            }

            return p;
        }

        function getGenresPara (genres)
        {
            var p, strong, t = "Genres: ";
            p = document.createElement("p");
            strong = document.createElement("strong");
            t = document.createTextNode(t);
            strong.appendChild(t);

            t = "";
            for (var i = 0, glen = genres.length; i < glen; i++) 
            {
                t += genres[i] + ", ";
            }

            if (t.length > 0)
            { 
                p.appendChild(strong);
                text = document.createTextNode(t.slice(0, -2));
                p.appendChild(text);
            } 
            return p;
        }

        var displayItem = function (item)
        {
            var itemDiv, itemDetailsDiv, h3, t, a;
            itemDiv = document.createElement("div");

            // composition
            a = getCompositionAnchor(item[0].composition);
            h3 = document.createElement("h3");
            h3.appendChild(a);
            var start = item[0].folios.start.label, end = item[0].folios.end.label;
            if ( start === item[0].folios.end.label)
            {
                t = document.createTextNode(" (" + start + ")");
            }
            else
            {
                t = document.createTextNode(" (" + start + "-" + end + ")");
            }
            h3.appendChild(t);

            itemDetailsDiv = document.createElement("div");

            // composer
            p = getComposersPara(item[0].composers);
            itemDetailsDiv.appendChild(p);

            // genres
            p = getGenresPara(item[0].composition.genres);
            itemDetailsDiv.appendChild(p);

            // voices
            p = getVoicesPara(item[0].voices);
            itemDetailsDiv.appendChild(p);

            itemDiv.appendChild(h3);
            itemDiv.appendChild(itemDetailsDiv);
            itemsDiv.appendChild(itemDiv);
        };

        var cacheAndDisplayItem = function (service)
        {
            return function (item)
            {
                items[service.id] = item;
                displayItem (item);
            };

        };

        var fetchItems = function (services)
        {
            for (var i = 0, slen = services.length; i < slen; i++)
            {
                var service = services[i];
                if (items[service.id])
                {
                    displayItem(items[service.id]);
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
            var t = document.createTextNode("Folio " + filename);
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
