import $ from 'jquery';
import bootstrap from 'twbs/bootstrap';
import 'fetch';

import { logOut } from 'app/auth';

function main()
{
    console.log('Initializing JavaScript');

    var logoutElement = document.getElementById('logout-link');
    if (logoutElement)
    {
        logoutElement.addEventListener('click', logOut);
    }
}

main();
