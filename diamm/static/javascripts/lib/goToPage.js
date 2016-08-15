var Page = function (divaInstance)
{
    var goToPage = function(pageName)
    {
        activeTabPanel = document.querySelector('.front');
        if (activeTabPanel)
            activeTabPanel.classList.remove('front');
        newActiveTabPanel = document.querySelector('#images');
        newActiveTabPanel.classList.add('front');

        divaInstance.gotoPageByName(pageName);
        // This is to make sure the diva viewer resizes on tab change
        // Will be a non-issue in diva 5
        window.dispatchEvent(new Event('resize'));
    }

    return function (params) {
        if (params['folio'])
        {
            if (!divaInstance.isReady())
            {
                var handle = diva.Events.subscribe(
                    'ViewerDidLoad',
                    function ()
                    {
                        goToPage(params['folio']);
                        diva.Events.unsubscribe(handle);
                    });
            }
            goToPage(params['folio']);
        }
    };
}
