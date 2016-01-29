import Cookie from './cookie';

export function logOut(event)
{
    /*
        This method treats the log-out link as a form
        submission, allowing us to use POST for the HTTP method
        (deleting a session on the server is a non-idemnpotent action).

        It will redirect to the home page on success.
     */
    var csrfcookie = new Cookie('csrftoken');
    fetch('/logout/', {
        method: 'post',
        credentials: 'same-origin',
        headers: {
            'Accept': "application/json",
            'X-CSRFToken': csrfcookie.value
        }
    }).then(function(response)
    {
        return response.json();
    }).then(function(body)
    {
        //redirect to the home page.
        document.location.replace("/");
    });

    event.preventDefault();
}
