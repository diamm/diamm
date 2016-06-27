var goToPage = function (pageName)
{
    activeTabPanel = document.querySelector(".front");
    activeTabPanel.classList.remove("front");
    newActiveTabPanel = document.querySelector("#images");
    newActiveTabPanel.classList.add("front");

    var diva_instance = $('#diva-wrapper').data('diva');
    console.log(diva_instance);
    diva_instance.gotoPageByName(pageName);
}
