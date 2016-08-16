function Hash () {
    console.log("Hash has been initialized");
    var that = this;

    this.callbacks = arguments;

    var getHashParams = function ()
    {
        var hash = window.location.hash.substr(1).split('&');

        var params = {};
        for (var i = 0, hlen = hash.length; i < hlen; i++)
        {
            h = hash[i].split("=");
            params[h[0]] = h[1];
        }
        return params;
    }

    var onHashChange = function()
    {
        params = getHashParams();
        for (var i = 0, clen = this.callbacks.length; i < clen; i++)
        {
            that.callbacks[i](params);
        }
    }

    onHashChange();
    window.onhashchange = onHashChange;
}
