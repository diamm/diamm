var Tab = function (params) {
    var goToTab = function (tabHash)
    {
        var activeTabPanel = document.querySelector('.front');
        if (activeTabPanel)
        {
            activeTabPanel.classList.remove('front');
        }
        var newActiveTabPanel = document.querySelector('#'+tabHash);
        newActiveTabPanel.classList.add('front');

        // This is to make sure the diva viewer resizers on tab change
        // Will be a non-issue in diva 5
        window.dispatchEvent(new Event('resize'));
    };

    if (params['tab'])
            goToTab(params['tab']);
};
