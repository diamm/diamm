(function($)
{
    var init = function ()
    {
        console.log('SaveSearch init called');
        var bookmarks = document.getElementsByClassName('save-search');
        var i = bookmarks.length

        while(i--)
        {
            var bookmark = bookmarks[i];
            handleClick(bookmark);
        }
    };

    var handleClick = function (bookmark)
    {
        bookmark.addEventListener('click', function(event)
        {
            event.preventDefault();
            save_search(bookmark);
        });
    };

    var toggle_bookmark = function (bookmark) {
        if (bookmark.dataset.save === "True")
        {
            bookmark.className = "save-search fa fa-bookmark";
            bookmark.setAttribute('data-save', 'False');
        }
        else
        {
            bookmark.className = "save-search fa fa-bookmark-o";
            bookmark.setAttribute('data-save', 'True');
        }
    }

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') 
        {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) 
            {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) 
                {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    var save_search = function (bookmark)
    {
        //TODO: handle case where save fails
        $.ajaxSetup({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        });
        $.ajax({
            url: "save",
            type: "POST",
            data: {
                query:  bookmark.dataset.query,
                query_type: bookmark.dataset.querytype,
                save: bookmark.dataset.save,
                id: bookmark.dataset.id
            },
            success: toggle_bookmark(bookmark),
            error: function(){
                console.log("Search save failed");
            }
        })
    };

    init();
})(jQuery);
