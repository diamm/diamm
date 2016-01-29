import { parseParams } from './app/utilities';

function facetFilter (event)
{
    var qstr = window.location.search.replace("?", "");
    var qstr_params = parseParams(qstr);

    console.log(qstr_params);

    var facetName = this.dataset.facetName;
    var facetValue = this.dataset.facetValue;

    console.debug(facetName);
    console.debug(facetValue);

    if (!(facetName in qstr_params))
    {
        var facetQ = facetName + "=" + facetValue;
        if (qstr != "")
        {
            // this makes sure that we either append the
            // querystring to an existing query string
            // (with a "&") or we just append it to the
            // existing URL.
            facetQ = "&" + facetQ;
        }
        window.location.search = qstr + facetQ;
    }
    event.preventDefault();
}

function init ()
{
    console.log('initializing search.');

    var filter_controls = document.getElementsByClassName('filter-type');

    //for (var filter of filter_controls)
    //{
    //    filter.addEventListener('click', facetFilter);
    //}
}

init();
