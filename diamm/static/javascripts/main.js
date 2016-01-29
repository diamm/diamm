function logOut(event)
{

    event.preventDefault();
}

var logoutElement = document.getElementById('logout-link');
logoutElement.addEventListener('click', logOut);
