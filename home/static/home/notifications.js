function toast({title = "", message = "", type = "info", duration = 3000}) {
    const main = document.getElementById("message");
    if (main) {
        const toast = document.createElement("div");

        // Auto remove toast
        const autoRemoveId = setTimeout(function () {
            main.removeChild(toast);
        }, duration + 1000);

        // Remove toast when clicked
        toast.onclick = function (e) {
            if (e.target.closest(".message__close")) {
                main.removeChild(toast);
                clearTimeout(autoRemoveId);
            }
        };

        const icons = {
            success: "fas fa-check-circle",
            info: "fas fa-info-circle",
            warning: "fas fa-exclamation-circle",
            error: "fas fa-exclamation-circle"
        };
        const icon = icons[type];
        const delay = (duration / 1000).toFixed(2);

        toast.classList.add("message", `message--${type}`);
        toast.style.animation = `slideInLeft ease .3s, fadeOut linear 1s ${delay}s forwards`;

        toast.innerHTML = `
                      <div class="message__icon">
                          <i class="${icon}"></i>
                      </div>
                      <div class="message__body">
                          <h3 class="message__title">${title}</h3>
                          <p class="message__msg">${message}</p>
                      </div>
                      <div class="message__close">
                          <i class="fas fa-times"></i>
                      </div>
                  `;
        main.appendChild(toast);
    }
}

function showSuccessAddToCart() {
    toast({
        title: "Success!",
        message: "Product added to cart successfully!",
        type: "success",
        duration: 5000
    });
}

function showErrorToast() {
    toast({
        title: "Error!",
        message: "Có lỗi xảy ra, vui lòng liên hệ quản trị viên.",
        type: "error",
        duration: 5000
    });
}

function showMissingInformation() {
    toast({
        title: "Error!",
        message: "Please fill in all the required information.",
        type: "error",
        duration: 5000
    });
}

function showProfileChanged() {
    toast({
        title: "Success!",
        message: "You have successfully updated the information.",
        type: "success",
        duration: 5000
    });
}

function showDeleteDefaultAddress() {
    toast({
        title: "Error!",
        message: "You cannot delete the default address.",
        type: "error",
        duration: 5000
    });
}

function showDeleteOptionalAddress() {
    toast({
        title: "Success!",
        message: "You have successfully deleted the address.",
        type: "success",
        duration: 5000
    });
}

$(".close-message").on("click", function () {
    $('#message').remove()
})

function showIncorrectPassword() {
    toast({
        title: "Error!",
        message: "Password confirmation does not match!",
        type: "error",
        duration: 5000
    });
}
function showIncorrectCurrentPassword() {
    toast({
        title: "Error!",
        message: "The old password is incorrect!",
        type: "error",
        duration: 5000
    });
}

function showPasswordChanged() {
    toast({
        title: "Success!",
        message: "You have successfully changed your password.",
        type: "success",
        duration: 5000
    });
}
function showMaximumOptionalAddress() {
    toast({
        title: "Error!",
        message: "Maximum of 2 optional addresses allowed!",
        type: "error",
        duration: 5000
    });
}
function showLoginToAddToCart() {
    toast({
        title: "Error!",
        message: "Please log in to add products!",
        type: "error",
        duration: 5000
    });
}