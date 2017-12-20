function showErrorToastOrRedirectToLoginWithNext(xhr) {
    if (xhr.status === 403 && xhr.responseText.indexOf('credentials were not provided') > -1) {
        window.location = '/accounts/login?next=/' + (location.pathname+location.search).substr(1);
    } else {
        showToast('There was an error', {type: 'error'})
    }
}

var TOKEN = getCookie('csrftoken');

function showToast(message, options) {
    options = options || {};
    message = message || 'No message';
    $.iaoAlert({
        msg: message,
        type: options.type || 'notification', // success error warning notification
        alertTime: '1500',
        position: 'top-right',
        mode: 'dark',
        fadeOnHover: true
    })
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ajax_request(data, options, cb) {
    data.csrfmiddlewaretoken = TOKEN;
    var url = options.url || [location.protocol, '//', location.host, location.pathname].join('');
    $.ajax({
        data: data,
        type: 'POST',
        url: url,
        success: function(response) {
            cb && cb();
            showToast(response.message);
            if (options.refresh) {
                window.location.reload(false);
            }
        },
        error: function(xhr, ajaxOptions, thrownErro) {
            showErrorToastOrRedirectToLoginWithNext(xhr);
        }
    });
}