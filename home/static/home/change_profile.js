$(document).ready(function () {
    $("#address-dropdown").change(function () {
        var selectedOption = $(this).find("option:selected");
        var street = selectedOption.data("street");
        var ward = selectedOption.data("ward");
        const district = selectedOption.data("district");
        var city = selectedOption.data("city");

        $("#inputStreet").val(street);
        $("#inputCity").val(city);
        var city_id = $("#inputCity option:selected").data("id")

        $('.districts').remove();

        function getDistricts() {
            return new Promise(function (resolve, reject) {
                if (city_id !== "*") {
                    $.ajax({
                        url: '/get_districts/',
                        method: 'GET',
                        data: {city_id: city_id},
                        success: function (data) {
                            let temp;
                            for (let key in data.items) {
                                temp = `<option class="districts"
                                value="${data.items[key].name}"
                                data-id="${data.items[key].id}">${data.items[key].name_with_type}</option>`;
                                $('#inputDistrict').append(temp)
                            }
                            $("#inputDistrict").val(district);

                            var district_id = $("#inputDistrict option:selected").data("id");
                            resolve(district_id);
                        },
                        error: function (error) {
                            console.log(error);
                            reject(error);
                        }
                    });
                } else {
                    resolve(null);
                }
            });
        }

        getDistricts().then(function (district_id) {
            $('.wards').remove();

            function getWards() {
                if (district_id !== "*") {
                    $.ajax({
                        url: '/get_wards/',
                        method: 'GET',
                        data: {district_id: district_id},
                        success: function (data) {
                            let temp;
                            for (let key in data.items) {
                                temp = `<option class="wards"
                                value="${data.items[key].name}"
                                data-id="${data.items[key].id}">${data.items[key].name_with_type}</option>`;
                                $('#inputWard').append(temp)
                            }
                            $("#inputWard").val(ward);
                        },
                        error: function (error) {
                            console.log(error);
                        }
                    });
                }
            }

            getWards()
        });
    });

    $("#inputCity").change(function getDistricts() {
        var city_id = $("#inputCity option:selected").data("id")
        if (city_id !== "*") {
            $('.districts').remove()
            $('.wards').remove()
            $.ajax({
                url: '/get_districts/',
                method: 'GET',
                data: {city_id: city_id},
                success: function (data) {
                    let temp;
                    for (let key in data.items) {
                        temp = `<option class="districts"
                                value="${data.items[key].name}"
                                data-id="${data.items[key].id}">${data.items[key].name_with_type}</option>`;
                        $('#inputDistrict').append(temp)
                    }
                },
                error: function (error) {
                    console.log(error);
                }
            });
        }
    })

    $("#inputDistrict").change(function getWards() {
        var district_id = $("#inputDistrict option:selected").data("id")
        if (district_id !== "*") {
            $('.wards').remove()
            $.ajax({
                url: '/get_wards/',
                method: 'GET',
                data: {district_id: district_id},
                success: function (data) {
                    let temp;
                    for (let key in data.items) {
                        temp = `<option class="wards"
                                value="${data.items[key].name}"
                                data-id="${data.items[key].id}">${data.items[key].name_with_type}</option>`;
                        $('#inputWard').append(temp)
                    }
                },
                error: function (error) {
                    console.log(error);
                }
            });
        }
    })

    $('#change-profile').on('click', function () {
        var first_name = $('#inputFirstName').val()
        var last_name = $('#inputLastName').val()
        var email = $('#inputEmailAddress').val()
        var phone_number = $('#inputPhone').val()
        var date_of_birth = $('#inputBirthday').val()

        var street = $('#inputStreet').val()
        var ward = $('#inputWard').val()
        var district = $('#inputDistrict').val()
        var city = $('#inputCity').val()

        let csrfToken = $('[name=csrfmiddlewaretoken]').val();

        var dropdown = document.getElementById("address-dropdown");
        var selectedAddress = dropdown.options[dropdown.selectedIndex];
        var action = selectedAddress.value
        var optional_id = selectedAddress.dataset.id;

        if ([first_name, last_name, street, ward, district, city, email, date_of_birth, phone_number].some(field => field.trim() === '')) {
            showMissingInformation()
        } else {
            $.ajax({
                method: 'POST',
                url: '/change-profile-user/',
                data: {
                    first_name: first_name,
                    last_name: last_name,
                    street: street,
                    ward: ward,
                    district: district,
                    city: city,
                    email: email,
                    phone_number: phone_number,
                    date_of_birth: date_of_birth,
                    action: action,
                    optional_id: optional_id,
                    csrfmiddlewaretoken: csrfToken,
                },
                dataType: 'json',
                success: function (response) {
                    showProfileChanged()
                    setTimeout(function () {
                        window.location.href = '/user/profile/';
                    }, 1000);
                },
                error: function (error) {
                    showMaximumOptionalAddress()
                }
            });
        }
    })

    $("#delete-profile-button").on("click", function () {
        var dropdown = document.getElementById("address-dropdown");
        var selectedAddress = dropdown.options[dropdown.selectedIndex];
        var action = selectedAddress.value
        var optional_id = selectedAddress.dataset.id;
        let csrfToken = $('[name=csrfmiddlewaretoken]').val();

        if (action === 'default') {
            showDeleteDefaultAddress()
        } else if (action === 'optional') {
            $.ajax({
                method: 'POST',
                url: '/delete-optional-address/',
                data: {
                    optional_id: optional_id,
                    csrfmiddlewaretoken: csrfToken,
                },
                dataType: 'json',
                success: function (response) {
                    showDeleteOptionalAddress()
                    setTimeout(function () {
                        window.location.href = '/user/profile/';
                    }, 1000);
                },
                error: function (error) {
                    console.log('error: ', error.message);
                }
            });
        }
    })
})


