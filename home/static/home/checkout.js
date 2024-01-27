function checkForm(e) {
    var street = $('#inputStreet').val()
    var ward = $('#inputWard').val()
    var district = $('#inputDistrict').val()
    var city = $('#inputCity').val()
    let csrfToken = $('[name=csrfmiddlewaretoken]').val();
    if (street.trim() === '' || ward.trim() === '' || district.trim() === '' || city.trim() === '') {
        showMissingInformation()
        e.preventDefault()
    } else {
        var checkbox = $("#saveAsDefaultAddress");
        if (checkbox.is(':checked')) {
            $.ajax({
                url: '/change-default-address/',
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: csrfToken,
                    street: street,
                    ward: ward,
                    district: district,
                    city: city,
                },
                success: function (data) {
                },
                error: function (error) {
                    console.log(error)
                }
            })
        }
    }
}

$("#checkout-btn").click(checkForm);