$(document).ready(function () {
    $("#card-container").on("click", ".update-btn", function (e) {
        iso.layout();
        let productId = this.dataset.product;
        let action = this.dataset.action;
        let quantity = this.dataset.value;
        let slug = this.dataset.slug;
        let object = this.dataset.object;
        //changeFunc(productId, action, quantity, slug);

        let data = { productId, action, quantity, slug };
        // Update cart item quantity
        let btn = "#update-btn-" + action + "-" + productId;

        e.preventDefault();
        $(btn).disabled = true;

        var csrfToken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            method: "POST",
            url: "/update-item/",
            data: {
                slug: data.slug,
                csrfmiddlewaretoken: csrfToken,
                action: action,
            },
            dataType: "json",
            success: function (response) {
                // Handle the AJAX response here
                let quantityDisplay = "#quantity-display-" + response.id;
                let totalPrice = "#total-price-" + response.id;
                let cardId = "#card" + response.id;

                if (response.quantity == 0) {
                    // Set timeout to delay the removal of the card
                    $(".container")
                        .find(quantityDisplay)
                        .text(response.quantity);
                    $(".container")
                        .find(totalPrice)
                        .text(response.price.toFixed(0) + "đ");

                    setTimeout(function () {
                        $(cardId).remove();
                        iso.layout();
                        $(".mb-0")
                            .find("#order-sum-cart")
                            .text(parseInt(response.sum));
                        $("#cart-item-count").text(parseInt(response.sum));
                    }, 20);
                } else {
                    $(".container")
                        .find(quantityDisplay)
                        .text(response.quantity);
                    $(".container")
                        .find(totalPrice)
                        .text(response.price.toFixed(0) + "đ");
                }
                // changeText(response.totalPrice.toFixed(2));
                $("#main-total").text(response.totalPrice.toFixed(0) + "đ");
            },
            error: function (error) {
                console.log("error", error);
            },
        });
    });

    $(".remove-btn").click(function (e) {
        let id = this.dataset.id;
        let slug = this.dataset.slug;

        let data = { id, slug };

        // Used to prevent default behavior of button
        e.preventDefault();

        // Csrf token is required for Django
        let csrfToken = $("[name=csrfmiddlewaretoken]").val();

        $.ajax({
            method: "POST",
            url: "/remove-from-cart/",
            data: {
                slug: data.slug,
                csrfmiddlewaretoken: csrfToken,
                id: data.id,
            },
            dataType: "json",
            success: function (response) {
                // Get card id to remove
                let cardId = "#card" + response.id;
                $(cardId).remove();
                $(".mb-0").find("#order-sum-cart").text(parseInt(response.sum));
                $("#cart-item-count").text(parseInt(response.sum));
                $("#main-total").text(response.totalPrice.toFixed(0) + "đ");
                iso.layout();
                // changeText(response.totalPrice.toFixed(2));
            },
            error: function (error) {
                console.log("error: ", error.message);
            },
        });
    });

    // Sorting function
    // init Isotope
    var iso = new Isotope(".grid", {
        itemSelector: ".card",
        layoutMode: "fitRows",
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
        // only sort-btn is clicked
        if (!matchesSelector(event.target, ".sort-btn")) {
            return;
        }

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
