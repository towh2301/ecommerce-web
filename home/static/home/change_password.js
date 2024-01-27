$("#change-password").on("click", function () {
    var current_password = $('#inputCurrentPassword').val();
    var new_password = $('#inputNewPassword').val();
    var confirm_new_password = $('#inputConfirmNewPassword').val();

    let csrfToken = $('[name=csrfmiddlewaretoken]').val();

    if (new_password !== confirm_new_password) {
        showIncorrectPassword()
    } else {
        $.ajax({
            method: 'POST',
            url: '/change-password/',
            data: {
                csrfmiddlewaretoken: csrfToken,
                current_password: current_password,
                new_password: new_password,
                confirm_new_password: confirm_new_password,
            },
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    showPasswordChanged();
                } else if (response.error) {
                    showIncorrectCurrentPassword()
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    }
})