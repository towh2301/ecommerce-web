$(document).ready(function () {
    // Click to show/hide billing info
    $(".card-custom").on("click", function (e) {
        $(".modal-content").find(".modal-div").remove(); // Remove all modal-div before append new one
        let data_id = this.dataset.id;
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            method: "POST",
            url: "get-payment-info/",
            data: {
                data_id: data_id,
                csrfmiddlewaretoken: csrfToken,
            },
            dataType: "json",
            success: function (data) {
                console.log(data.id);
                console.log(data.items);
                console.log(data.total_price);
                let items = data.items;
                let item_html = $("<div class='modal-div'></div>");
                for (let i = 0; i < items.length; i++) {
                    console.log(items[i].title);

                    let item = items[i];

                    // Get item info
                    let item_quantity = item.quantity;
                    let price = item.price_each;
                    let item_name = item.slug;
                    let item_title = item.title;
                    console.log(item_title)
                    let img = item.img;
                    let id = item.id;
                    let status = data.status;

                    // Append item info to modal
                    if (status != "paid") {
                        item_html.append(`<div class=\"row modal${id}\" id=\"item-row-modal\">
                    <input type=\"hidden\" name=\"price-each-${id}\" value=\"${price}\">
                    <img src="${img}"
                    class="col-3 img-fluid rounded-3 product-img-billing" alt="Shopping item">
                        <div class=\"col-2\">${item_title}</div>
                        <div class=\"col-3\" id=\"generated-quan\">
                            <button class=\"btn btn-sm plus-btn\" data-id="${id}" data-action=\"plus\" data-payment=\"${
                            data.id
                        }\" data-group=\"edit\">
                                <i class="fa-solid fa-plus"></i>
                            </button>
                                <b id=\"quan-${id}\">${item_quantity}</b>
                            <button class=\"btn btn-sm minus-btn\" data-id="${id}" data-action=\"minus\"  data-payment=\"${
                            data.id
                        }\" data-group=\"edit\">
                                <i class="fa-solid fa-minus"></i>
                            </button>
                        </div>
                        <div class=\"col-2\" id=\"item-total-price-${id}\">
                            Tổng: ${item_quantity * price}
                        </div>
        
                        <div class=\"col-2\">
                            <button class=\"btn btn-outline-danger btn-sm delete-btn float-right\" data-id="${id}" data-action=\"delete-item\" data-payment=\"${
                            data.id
                        }\" data-group=\"edit\">
                                Xoá
                            </button>
                        </div>   
                    </div>`);
                    } else {
                        item_html.append(`<div class=\"row modal${id}\" id=\"item-row-modal\">
                    <input type=\"hidden\" name=\"price-each-${id}\" value=\"${price}\">
                    <img src="${img}"
                    class="col-3 img-fluid rounded-3 product-img-billing" alt="Shopping item">
                        <div class=\"col-2\">${item_title}</div>
                        <div class=\"col-3\" id=\"generated-quan\">
                            <button class=\"btn btn-sm plus-btn\" data-id="${id}" data-action=\"plus\" data-payment=\"${
                            data.id
                        }\" data-group=\"edit\" disabled>
                                <i class="fa-solid fa-plus"></i>
                            </button>
                                <b id=\"quan-${id}\">${item_quantity}</b>
                            <button class=\"btn btn-sm minus-btn\" data-id="${id}" data-action=\"minus\"  data-payment=\"${
                            data.id
                        }\" data-group=\"edit\" disabled>
                                <i class="fa-solid fa-minus"></i>
                            </button>
                        </div>
                        <div class=\"col-2\" id=\"item-total-price-${id}\">
                            Tổng: ${item_quantity * price}
                        </div>
        
                        <div class=\"col-2\">
                            <button class=\"btn btn-outline-danger btn-sm delete-btn float-right\" data-id="${id}" data-action=\"delete-item\" data-payment=\"${
                            data.id
                        }\" data-group=\"edit\" disabled>
                                Xoá
                            </button>
                        </div>   
                    </div>`);
                    }
                }
                //

                $(".modal-content").append(item_html);
            },
            error: function (error) {
                console.log(error.error);
            },
        });

        e.preventDefault();
        $("#itemModal").addClass("active");
        $("#itemModal").show();
    });

    $("#itemModal").on("click", ".close-btn", function (event) {
        $("#itemModal").hide(); // Close the modal when clicked close-btn
        $("#itemModal").find(".modal-div").remove();
        $("#itemModal").removeClass("active");
    });

    $(window).on("click", function (event) {
        if (event.target == $("#itemModal")[0]) {
            $("#itemModal").hide();
            $("#itemModal").find(".modal-div").remove(); // Close the modal when clicked outside
        }
    });

    // Button action control
    $(".remove-button").click(function (e) {
        // Prevent the card-custom click logic from firing
        e.preventDefault();
        e.stopPropagation();
        let data_id = this.dataset.id;
        let data_action = this.dataset.action;
        let data = { id: data_id, action: data_action };
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();
        console.log(data_id);

        doAjax(data, csrfToken, 0);
    });

    $(".pay-button").click(function (e) {
        e.stopPropagation();
        let data_id = this.dataset.id;
    });

    $("#itemModal").on("click", ".delete-btn", function (e) {
        e.stopPropagation();
        let data_id = this.dataset.payment;
        let item_id = this.dataset.id;
        let data_action = this.dataset.action;
        let data_group = this.dataset.group;
        let data = {
            id: data_id,
            action: data_action,
            item_id: item_id,
            group: data_group,
        };
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();

        doAjax(data, csrfToken, 0);
    });

    $("#itemModal").on("click", ".plus-btn", function (e) {
        let data_id = this.dataset.payment;
        let item_id = this.dataset.id;
        let data_action = this.dataset.action;
        let data_group = this.dataset.group;
        let price_each = $(`[name=price-each-${item_id}]`).val();
        let data = {
            id: data_id,
            action: data_action,
            item_id: item_id,
            group: data_group,
        };
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();
        doAjax(data, csrfToken, price_each);
    });

    $("#itemModal").on("click", ".minus-btn", function (e) {
        let data_id = this.dataset.payment;
        let item_id = this.dataset.id;
        let data_action = this.dataset.action;
        let data_group = this.dataset.group;
        let price_each = $(`[name=price-each-${item_id}]`).val();
        let data = {
            id: data_id,
            action: data_action,
            item_id: item_id,
            group: data_group,
        };
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();
        doAjax(data, csrfToken, price_each);
    });

    let doAjax = function (data, csrfToken, price_each) {
        $.ajax({
            method: "POST",
            url: "alter-payment/",
            data: {
                data: JSON.stringify(data),
                csrfmiddlewaretoken: csrfToken,
            },
            dataType: "json",
            success: function (data) {
                console.log(data);

                // Remove card if cancel button is clicked
                if (data.action === "cancel") {
                    $(`[data-id=${data.id}]`).remove();
                }

                // Remove item if delete button is clicked
                if (data.action === "delete-item") {
                    let itemClass = `.modal${data.item_id}`;
                    $(itemClass).remove();
                    let payment_id = `#total-${data.id}`;
                    $(".row")
                        .find(payment_id)
                        .text(data.total + "");
                    if (data.is_blank) {
                        $(`[data-id=${data.id}]`).remove();
                    }
                }

                // Plus button
                if (data.action === "plus") {
                    let itemQuantity = data.quantity;
                    let itemPrice = data.price;
                    $("#quan-" + data.item_id).text(itemQuantity);
                    let payment_id = `#total-${data.id}`;
                    $(".row")
                        .find(payment_id)
                        .text(data.total + "");
                    $("#item-total-price-" + data.item_id).text(
                        "Tổng: " + itemQuantity * price_each + ""
                    );
                }

                // Minus button
                if (data.action === "minus") {
                    let itemQuantity = data.quantity;
                    let itemPrice = data.price;
                    $("#quan-" + data.item_id).text(itemQuantity);
                    let payment_id = `#total-${data.id}`;

                    if (itemQuantity == 0) {
                        let itemClass = `.modal${data.item_id}`;
                        $(itemClass).remove();
                    } else {
                        $("#item-total-price-" + data.item_id).text(
                            "Tổng: " + itemQuantity * price_each
                        );
                    }

                    $(".row")
                        .find(payment_id)
                        .text(data.total + "");
                    if (data.is_blank) {
                        $(`[data-id=${data.id}]`).remove();
                    }
                }
                iso.layout();
            },
            error: function (error) {
                console.log(error.error);
            },
        });
    };

    // Sorting function
    var iso = new Isotope(".grid", {
        itemSelector: ".card",
        //layoutMode: "fitRows",
        layoutMode: "masonry",
        percentPosition: true,
        transitionDuration: "0.3s",
        getSortData: {
            price: function (itemElem) {
                var price = itemElem.querySelector(".total-price").textContent;
                return parseFloat(price.replace(/[\(\)]/g, ""));
            },
        },
    });

    // bind sort button click
    var sortBtn = document.querySelector(".sort-btn");
    sortBtn.addEventListener("click", function (event) {
        iso.reloadItems();
        iso.layout();
        // only sort-btn is clicked
        if (!matchesSelector(event.target, ".sort-btn")) {
            return;
        }
        iso.reloadItems();
        iso.layout();

        // Sort by price follow ascending or descending
        if (sortBtn.classList.contains("is-checked")) {
            iso.arrange({ sortBy: "price", sortAscending: true });
        } else {
            iso.arrange({ sortBy: "price", sortAscending: false });
        }

        // Update sort data and SortBtn class
        iso.updateSortData();
        onSortButtonClick(event);
        iso.layout();
    });

    let sortIcon = document.querySelector(".sort-icon");
    function onSortButtonClick(event) {
        // only button clicks
        if (!matchesSelector(event.target, ".sort-btn")) {
            return;
        }

        var button = event.target;
        if (button.classList.contains("is-checked")) {
            button.classList.remove("is-checked");
            sortIcon.classList.remove("fa-angle-down");
            sortIcon.classList.add("fa-angle-up");
        } else {
            button.classList.add("is-checked");
            sortIcon.classList.remove("fa-angle-up");
            sortIcon.classList.add("fa-angle-down");
        }
    }
});
