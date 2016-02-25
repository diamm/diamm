(function ($)
{
    window.divaPlugins.push((function ()
    {
        var settings = {};
        var OTHER_CONTENT_KEY = "iiif-other-content";

        return {
            init: function (divaSettings, divaInstance)
            {
                console.log('Initializing Diva IIIF Plugin.');
                divaSettings.parentObject.data(OTHER_CONTENT_KEY, {});

                var checkStatus = function (response)
                {
                    if (response.status >= 200 && response.status < 300)
                    {
                        return response;
                    }
                };

                var getCanvas = function (pageIndex, filename, selector)
                {
                    var otherContentObject = divaSettings.parentObject.data(OTHER_CONTENT_KEY);

                    /*
                        If the object has been loaded before, get it from the cache.
                     */
                    if (otherContentObject.hasOwnProperty(pageIndex))
                    {
                        diva.Events.publish("IIIFPageDataDidLoad", [otherContentObject[pageIndex]], divaSettings.ID);
                        return;
                    }

                    /*
                        If not cached, we need to load it via HTTP Request
                     */
                    var canvases = settings.manifest.sequences[0].canvases;

                    if (canvases[pageIndex].hasOwnProperty('otherContent') && canvases[pageIndex].otherContent !== null)
                    {
                        var otherContent = canvases[pageIndex].otherContent[0];

                        if (otherContent.hasOwnProperty("@id"))
                        {
                            fetch(otherContent["@id"])
                                .then(checkStatus)
                                .then(function(response)
                                {
                                    return response.json()
                                })
                                .then(function(data)
                                {
                                    otherContentObject[pageIndex] = data;
                                    diva.Events.publish("IIIFPageDataDidLoad", [data], divaSettings.ID);
                                })
                        }
                    }
                };

                var setManifest = function (manifest)
                {
                    settings.manifest = manifest;
                };

                diva.Events.subscribe("ManifestDidLoad", setManifest, divaSettings.ID);
                diva.Events.subscribe("PageWillLoad", getCanvas, divaSettings.ID);
            },
            destroy: function ()
            {
                divaSettings.parentObject.removeData(OTHER_CONTENT_KEY);
            },
            pluginName: 'IIIFPageData',
            titleText: 'Extract and load extra content from IIIF manifests'
        };
    })());
})(jQuery);
