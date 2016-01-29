
/*
 * ES6 Port of the Cappuccino CPCookie Class.
 *
 *
 **/
class Cookie
{
    constructor(aName)
    {
        this._cookieName = aName;
        this._cookieValue = this._readCookieValue();
        this._expires = null;
    }

    get name()
    {
        return this._cookieName;
    }

    get value()
    {
        return this._cookieValue;
    }

    get expires()
    {
        return this._expires;
    }

    _readCookieValue()
    {
        var name = this._cookieName + '=',
            ca = document.cookie.split(';');

        for (var i = 0, len = ca.length; i < len; i++)
        {
            var c = ca[i];
            while (c.charAt(0) === ' ')
            {
                c = c.substring(1, c.length);
            }

            if (c.indexOf(name) === 0)
            {
                return c.substring(name.length, c.length);
            }
        }
        return '';
    }
}

export default Cookie;
