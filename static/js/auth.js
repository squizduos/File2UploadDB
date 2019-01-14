$(document).ready(function () {
    function getCookie(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    $.fn.serializeFormJSON = function () {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function () {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    $.ajaxSetup({
        beforeSend: function (xhr) {
            xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
        }
    });


    $('#admin-register-form').submit(function (event) {
        event.preventDefault();
        $.ajax({
            url: $(this).attr('action'),
            method: $(this).attr('method'),
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify($(this).serializeFormJSON()),
            success: function (data) {
                if (data['registered'] == true) {
                    $("#admin-register-success").removeAttr("hidden");
                    $("#admin-register-success").text("User is successfully added!");
                } else {
                    $("#admin-register-error").removeAttr("hidden");
                    $("#admin-register-error").text("Can not send mail!");
                }
            },
            error: function (data) {
                $("#admin-register-error").removeAttr("hidden");
                if ("non_field_errors" in data.responseJSON) {
                    $("#admin-register-error").text(data.responseJSON["non_field_errors"]);
                } else {
                    $("#admin-register-error").text("Unable to register user; check form for errors");
                }
            }
        });
    });

    $('#register-form').submit(function (event) {
        event.preventDefault();
        $.ajax({
            url: $(this).attr('action'),
            method: $(this).attr('method'),
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify($(this).serializeFormJSON()),
            success: function (data) {
                if (data['registered'] == true) {
                    window.location.href = "/";
                } else {
                    $("#register-errors").removeAttr("hidden");
                    $("#register-errors").text("Unable to register user; try again later.");
                }
            },
            error: function (data) {
                $("#register-errors").removeAttr("hidden");
                if ("non_field_errors" in data.responseJSON) {
                    $("#register-errors").text(data.responseJSON["non_field_errors"]);
                } else {
                    $("#register-errors").text(data.responseJSON);
                }
            }
        });
    });

});