export const FETCH_SOURCE_INFO = "FETCH_SOURCE_INFO";
export const RECEIVE_SOURCE_INFO = "RECEIVE_SOURCE_INFO";
export const SET_USER_INFO = "SET_USER_INFO";

export function setUserInfo (username, authenticated, staff, superuser)
{
    const isStaff = staff === "True";
    const isSuperuser = superuser === "True";
    const isAuthenticated = authenticated === "True";

    return {
        type: SET_USER_INFO,
        payload: {
            username,
            isAuthenticated,
            isStaff,
            isSuperuser
        }
    }
}

export function receiveSourceInfo (payload)
{
    console.log('dispatched receive source info');
    return {
        type: RECEIVE_SOURCE_INFO,
        payload
    }
}


export function fetchSourceInfo (sourceId)
{
    console.log('Fetching source info for ', sourceId);

    return (dispatch) =>
    {
        return fetch(`//alpha.diamm.ac.uk/sources/${sourceId}/`, {
                headers: {
                    "Accept": "application/json"
                }
            })
            .then((response) => {
                console.log('received response');
                return response.json();
            })
            .then((payload) => {
                console.log('dispatching');
                console.log(payload);
                dispatch(receiveSourceInfo(payload));
            });
    };
}
