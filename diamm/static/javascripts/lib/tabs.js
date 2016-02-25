(function($)
{
    var Tabs = function (element, options)
    {
        var parentObject = $(element);
        var activeTabPanel = null;

        var defaults = {
            tabsID: "tabs",                   // id of the parent tab block
            tabClass: "tab",                  // class of the <li> for each tab.
            tabContainerID: "tab-container",  // ID of the tab container block
            tabPanelClass: "tab-panel",       // class of the div for each tab panel.
            tabCallbacks: {}                  // a hash of callbacks to call when a tab panel is switched. Format: {hash: function}
        };

        var settings = $.extend({}, defaults, options);

        var init = function ()
        {
            console.log('tab init called');
            var tabParent = document.getElementById(settings.tabsID);
            var tabs = tabParent.querySelectorAll("a.tab"),
                i = tabs.length;

            while(i--)
            {
                var tab = tabs[i];
                handleClick(tab);
                if (tab.classList.contains('active'))
                {
                    gotoTab(tab.hash);
                }
            }
        };

        var handleClick = function (tab)
        {
            tab.addEventListener('click', function(event)
            {
                event.preventDefault();
                gotoTab(tab.hash);
            });
        };

        var gotoTab = function (tabHash)
        {
            if (activeTabPanel)
            {
                activeTabPanel.classList.remove('front');
            }
            var newActiveTabPanel = document.querySelector(tabHash);
            newActiveTabPanel.classList.add('front');
            activeTabPanel = newActiveTabPanel;

            if (settings.tabCallbacks.hasOwnProperty(tabHash))
            {
                settings.tabCallbacks[tabHash]();
            }
        };

        init();
    };

    $.fn.tabs = function (options)
    {
        return this.each(function ()
        {
            var tabContainer = $(this);

            var tabs = new Tabs(this, options);
            tabContainer.data('tabs', tabs);
        })
    }
})(jQuery);
