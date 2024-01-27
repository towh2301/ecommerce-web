$(document).ready(function () {

    // Tự động load trang sản phẩm đầu tiên
    loadPage(1, 'load-items-data-view', null);

    // Tạo function loadPage
    function loadPage(pageNumber, url, requestData) {
        requestData = requestData || {};
        requestData.page = pageNumber;

        $.ajax({
            url: `/${url}/?page=${pageNumber}`,
            method: 'GET',
            data: requestData,
            success: function (data) {
                var items = data.items;
                var hasNext = data.has_next;
                var hasPrevious = data.has_previous;
                var currentPage = data.page_number;
                $(".row.grid").empty();
                for (var key in items) {
                    var temp = `
                        <div class="col-sm-6 col-lg-4 all ${items[key].category}">
                        <input class="item-slug" value="${items[key].slug}" type="hidden">
                        <input class="item-quantity" value="1" type="hidden">
                            <div class="box">
                                ${items[key].discount ? `<div class="label"><p>${items[key].discount}% OFF</p></div>` : ''}                 
                                <div>
                                    <div class="img-box">                                 
                                        <a href="${items[key].get_absolute_url}"><img src="${items[key].image}" alt=""></a>                
                                    </div>
                                    <div class="detail-box">
                                        <h5>
                                            ${items[key].title}
                                        </h5>
                                        <p>
                                            ${items[key].description}
                                        </p>
                                        <div class="options">
                                            <h6>
                                                ${items[key].discount ? `<s>${items[key].price}đ</s> ${items[key].get_final_price}đ` : `${items[key].get_final_price}đ`}  
                                            </h6>
                                            <a href="" class="add-to-cart">
                                                <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
                                                     xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
                                                     viewBox="0 0 456.029 456.029"
                                                     style="enable-background:new 0 0 456.029 456.029;" xml:space="preserve">
                                <g>
                                  <g>
                                    <path d="M345.6,338.862c-29.184,0-53.248,23.552-53.248,53.248c0,29.184,23.552,53.248,53.248,53.248
                                 c29.184,0,53.248-23.552,53.248-53.248C398.336,362.926,374.784,338.862,345.6,338.862z"/>
                                  </g>
                                </g>
                                                    <g>
                                  <g>
                                    <path d="M439.296,84.91c-1.024,0-2.56-0.512-4.096-0.512H112.64l-5.12-34.304C104.448,27.566,84.992,10.67,61.952,10.67H20.48
                                 C9.216,10.67,0,19.886,0,31.15c0,11.264,9.216,20.48,20.48,20.48h41.472c2.56,0,4.608,2.048,5.12,4.608l31.744,216.064
                                 c4.096,27.136,27.648,47.616,55.296,47.616h212.992c26.624,0,49.664-18.944,55.296-45.056l33.28-166.4
                                 C457.728,97.71,450.56,86.958,439.296,84.91z"/>
                                  </g>
                                </g>
                                                    <g>
                                  <g>
                                    <path d="M215.04,389.55c-1.024-28.16-24.576-50.688-52.736-50.688c-29.696,1.536-52.224,26.112-51.2,55.296
                                 c1.024,28.16,24.064,50.688,52.224,50.688h1.024C193.536,443.31,216.576,418.734,215.04,389.55z"/>
                                  </g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                                                    <g>
                                </g>
                              </svg>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `
                    $(".row.grid").append(temp)
                }

                // Update the pagination control
                $('.page-item').empty()

                if (hasPrevious) {
                    $('#first-page-div').append(
                        `<button id="first-page-button" class="page-link"><span aria-hidden="true">&laquo;</span></button>`
                    );
                    $('#previous-div').append(
                        `<button id="prev-button" class="page-link"><span aria-hidden="true">&#8249;</span></button>`
                    );
                }
                if (hasNext) {
                    $('#next-div').append(
                        `<button id="next-button" class="page-link"><span aria-hidden="true">&#8250;</span></button>`
                    );
                    $('#last-page-div').append(
                        `<button id="last-page-button" class="page-link"><span aria-hidden="true">&raquo;</span></button>`
                    );
                }


                $('#current-page').html(currentPage)

                // Attach click event handlers to the buttons
                $('#prev-button').on('click', function () {
                    if (currentPage > 1) {
                        currentPage--;
                        loadPage(currentPage, url, requestData);
                    }
                });

                $('#next-button').on('click', function () {
                    if (data.has_next) {
                        currentPage++;
                        loadPage(currentPage, url, requestData);
                    }
                });
                $('#first-page-button').on('click', function () {
                    loadPage(1, url, requestData);
                });
                $('#last-page-button').on('click', function () {
                    loadPage(data.num_pages, url, requestData);
                });
            },
            error: function (error) {
                console.log(error);
            }
        });
    }

    // Load sản phẩm khi tìm kiếm
    $("#search-form").submit(function (event) {
        event.preventDefault();

        var query = $('#search-input').val();
        $(".select-category-btn").removeClass("active");
        $("#all-categories").addClass("active");

        loadPage(1, 'search-item', {query: query});
    });

    // Load sản phẩm khi chọn category
    $(".select-category-btn").click(function () {
        $(".select-category-btn").removeClass("active");
        $(this).addClass("active");
        $("#search-input").val('')
        var category = this.dataset.filter;
        loadPage(1, 'categories', {category: category});
    });

});

