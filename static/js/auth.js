$(document).ready(function() {
    $('#login-form').ajaxForm({
        success: function(data) {
            localStorage.token = data['key'];
            window.location.href = "/";
        },
        error: function(data) {
            $("#login-error").removeAttr("hidden");
            if ("non_field_errors" in data.responseJSON) {
                $("#login-error").text(data.responseJSON["non_field_errors"]);
            } else if ("login_errors" in data.responseJSON) {
                $("#login-error").text(data.responseJSON["login_errors"]);
            } else {
                $("#login-error").text("Unable to login; check form for errors");
            }
        }
    });

    $('#admin-register-form').ajaxForm({
        beforeSend: function(xhr) {
            $("#admin-register-success").attr("hidden", "true");
            $("#admin-register-error").attr("hidden", "true");
            xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
        },
        success: function(data) {
            if (data['registered'] == true) {
                $("#admin-register-success").removeAttr("hidden");
                $("#admin-register-success").text("User is successfully added!");
            } else {
                $("#admin-register-error").removeAttr("hidden");
                $("#admin-register-error").text("Can not send mail!");
            }
        },
        error: function(data) {
            $("#admin-register-error").removeAttr("hidden");
            if ("non_field_errors" in data.responseJSON) {
                $("#admin-register-error").text(data.responseJSON["non_field_errors"]);
            } else {
                $("#admin-register-error").text("Unable to register user; check form for errors");
            }
        }
    });

    $('#register-form').ajaxForm({
        beforeSend: function(xhr) {
            $("#register-errors").attr("hidden", "true");
            xhr.setRequestHeader("Authorization", "Token " + localStorage.token);

        },
        success: function(data) {
            if (data['registered'] == true) {
                window.location.href = "/";
            } else {
                $("#register-errors").removeAttr("hidden");
                $("#register-errors").text("Unable to register user; try again later.");
            }
        },
        error: function(data) {
            $("#register-errors").removeAttr("hidden");
            if ("non_field_errors" in data.responseJSON) {
                $("#register-errors").text(data.responseJSON["non_field_errors"]);
            } else {
                $("#register-errors").text(data.responseJSON);
            }
        }
    });
});