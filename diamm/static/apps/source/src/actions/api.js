import {
    SERVER_BASE_URL
} from "../constants";

function post (endpoint, body, callback=null)
{
    return (dispatch) =>
    {
        let url = `${SERVER_BASE_URL}${endpoint}`;
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        })
        .then( (response) =>
        {
            if (callback)
            {
                callback(response.json())
            }
        })
    }
}
