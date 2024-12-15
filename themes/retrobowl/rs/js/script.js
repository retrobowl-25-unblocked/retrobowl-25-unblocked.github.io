// ============================ search ================================= 
$('.search-form__btn').on('click', function () {
    gameSearch()
})

$('.search-form__input').on('keyup', function (e) {
    if (e.key === 'Enter' || e.keyCode === 13) {
        gameSearch()
    }
})

function gameSearch() {
    let keywords = $(".search-form__input").val();
    var rex_rule = /[ \-\.?:\\\/\_\'\*]+/g;
    var value1 = keywords.replace(rex_rule, " ").trim().toLowerCase();
    value1 = value1.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    var url = '/search/' + value1;
    if (value1 && oldValue != value1) {
        oldValue = value1;
        window.location.href = url;
    }
}

// ============================ paging vs click pagination.php + show gif loading ================================= 
function paging(p) {
    $(".loading_mask").removeClass("hidden-load");
    if (!p) {
        p = 1;
    }

    // Load từ file HTML tĩnh thay vì gọi AJAX
    fetch(`./pages/page-${p}.html`)
        .then(response => response.text())
        .then(html => {
            $(".loading_mask").addClass("hidden-load");
            $("#ajax-append").html(html);

            // Khởi tạo lazy loading cho images
            let t = [].slice.call(document.querySelectorAll("img.lazy-image"));
            if ("IntersectionObserver" in window) {
                let e = new IntersectionObserver(function (t, n) {
                    t.forEach(function (t) {
                        if (t.isIntersecting) {
                            let n = t.target;
                            n.dataset.src && ((n.src = n.dataset.src), n.classList.remove("lazy-image"), e.unobserve(n));
                        }
                    });
                });
                t.forEach(function (t) {
                    e.observe(t);
                });
            }
        })
        .catch(error => {
            console.error('Error loading page:', error);
            $(".loading_mask").addClass("hidden-load");
        });
}

$(document).ready(function () {
    addPlugin();
})

// ajax full_rate + comment
function addPlugin() {
    if (!id_game && !url_game) {
        return
    }
    // Load từ file HTML tĩnh cho plugin
    fetch('./plugins/plugin.html')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            $("#append-rate").html(doc.querySelector('#rate-content').innerHTML);
            $("#append-comment").html(doc.querySelector('#comment-content').innerHTML);
        })
        .catch(error => console.error('Error loading plugin:', error));
}

// ===========================  Show more / Show less =======================================
$('.btn-showmore').click(function () {
    if ($('.desc-text').hasClass('desc-text-full')) {
        $('.desc-text').removeClass('desc-text-full');
        $('.btn-showmore').html("Show more »");
        $('html, body').animate({
            scrollTop: $('.area__column--content').offset().top
        }, 500);
    } else {
        $('.desc-text').addClass('desc-text-full');
        $('.btn-showmore').html("Show less «");
    }
})