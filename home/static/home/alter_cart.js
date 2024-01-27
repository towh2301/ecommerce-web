$(document).ready(function () {
    // Add to cart
    $(".filters-content").on("click", ".add-to-cart", function (e) {
        e.preventDefault();
        let slug = $(this).closest(".all").find(".item-slug").val();
        let quantity = $(".item-quantity").val();
        csrfToken = $("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            url: "/add-to-cart/",
            type: "POST",
            data: {
                slug: slug,
                quantity: quantity,
                csrfmiddlewaretoken: csrfToken,
            },
            dataType: "json",
            success: function (response) {
                showSuccessAddToCart();
                $("#cart-item-count").text(parseInt(response.cart_item_count));
            },
            error: function (error) {
                showLoginToAddToCart();
            },
        });
    });

    //Order-now
    $(".offer_container").on("click", ".order-now", function (e) {
        e.preventDefault();
        let slug = $(this).closest(".detail-box").find(".item-slug").val();
        let quantity = $(".item-quantity").val();
        csrfToken = $("[name=csrfmiddlewaretoken]").val();
        $.ajax({
            url: "/add-to-cart/",
            type: "POST",
            data: {
                slug: slug,
                quantity: quantity,
                csrfmiddlewaretoken: csrfToken,
            },
            dataType: "json",
            success: function (response) {
                showSuccessAddToCart();
                $("#cart-item-count").text(parseInt(response.cart_item_count));
            },
            error: function (error) {
                showLoginToAddToCart();
            },
        });
    });

    $(".increase-quantity-btn").on("click", function () {
        var quantity = parseInt($(".item-quantity").val());
        quantity = quantity + 1;
        $(".item-quantity").val(quantity);
    });

    $(".decrease-quantity-btn").on("click", function () {
        var quantity = parseInt($(".item-quantity").val());
        if (quantity > 1) quantity = quantity - 1;
        $(".item-quantity").val(quantity);
    });
});
