var Page = function (params) {
    var goToPage = function(pageName)
    {
        activeTabPanel = document.querySelector('.front');
        activeTabPanel.classList.remove('front');
        newActiveTabPanel = document.querySelector('#images');
        newActiveTabPanel.classList.add('front');

        var diva_instance = $('#diva-wrapper').data('diva');
        diva_instance.gotoPageByName(pageName);
        // This is to make sure the diva viewer resizes on tab change
        // Will be a non-issue in diva 5
        window.dispatchEvent(new Event('resize'));
    }

    if (params['folio'])
        goToPage(params['folio']);
}
