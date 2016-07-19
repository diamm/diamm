var goToPage = function()
{
    var _onFolioClick = function (pageName)
    {
        return function()
        {
            activeTabPanel = document.querySelector(".front");
            activeTabPanel.classList.remove("front");
            newActiveTabPanel = document.querySelector("#images");
            newActiveTabPanel.classList.add("front");

            var diva_instance = $('#diva-wrapper').data('diva');
            diva_instance.gotoPageByName(pageName);
            // This is to make sure the diva viewer resizes on tab change
            // Will be a non-issue in diva 5
            window.dispatchEvent(new Event("resize"));
        }
    }

    var folio_links = document.querySelectorAll('.folio-link');
    for (var i=0, len=folio_links.length; i < len; i++)
    {
        page = folio_links[i].dataset.page;
        folio_links[i].addEventListener("click", _onFolioClick(page) )
    }

}
