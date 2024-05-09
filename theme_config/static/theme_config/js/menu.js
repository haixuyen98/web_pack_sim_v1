var currentMenuEditItem = null;
window.addEventListener('load',function() {
    $('#menu-editor').sortable({
        ghostClass: 'bg-success',
        animation: 150,
        stop: function (evt) {
            getMenuJson();
        }
    });
})
function removeMenuItem(__this) {
    __this.closest('.list-group-item').remove();
    getMenuJson();
}
function editMenuItem(__this) {
    currentMenuEditItem = __this.closest('.list-group-item');
    $('#form-add-menu').find('input[name="menu_link"]').val(currentMenuEditItem.attr('data-link'));
    $('#form-add-menu').find('input[name="menu_name"]').val(currentMenuEditItem.attr('data-name'));
    $('#menu-modal').modal('show');
}
function addMenuItem(panelId) {
    el = document.getElementById(panelId);
    el.classList.remove('theme-editor__panel--is-visible')
    el.classList.remove('theme-editor__panel--is-active')
}
function saveMenuForm() {
    var menuUrl = $('#form-add-menu').find('input[name="menu_link"]').val();
    var menuName = $('#form-add-menu').find('input[name="menu_name"]').val();
    if (menuName == '') {
        alert("Vui lòng điền tiêu đề menu");
        $('#form-add-menu').find('input[name="menu_name"]').focus();
        return;
    }
    if (menuUrl == '') {
        alert("Vui lòng nhập đường dẫn");
        $('#form-add-menu').find('input[name="menu_link"]').focus();
        return;
    }
    if (currentMenuEditItem == null) {
        var menuHtml = '<div class="list-group-item" data-name="' + menuName + '" data-link="' + menuUrl + '"><div class="row"><div class="col-md-9 name"><img class="icon_move" src="https://doan.websim.vn/images/Move.png" alt=""> <span class="mname">' + menuName + '</span></div><div class="col-md-3 remove"><a href="javascript:void(0)" onclick="editMenuItem($(this))"><i class="las la-pen"></i></a><a href="javascript:void(0)" onclick="removeMenuItem($(this))"><i class="las la-trash-alt"></i></a></div></div></div>';
        $('#menu-editor').append(menuHtml);
    } else {
        $(currentMenuEditItem).attr('data-name', menuName);
        $(currentMenuEditItem).attr('data-link', menuUrl);
        $(currentMenuEditItem).find('.mname').html(menuName);
        currentMenuEditItem = null;

    }
    getMenuJson();
    $('#menu-modal').modal('hide');
    $('#menu-modal').find("input[type=text], textarea").val("");
}

function getMenuJson() {
    var dataResponse = [];
    var element = $('#menu-editor .list-group-item');
    $(element).parent().find('.list-group-item').each(function () {
        $(this).attr('data-id', $(this).index() + 1);
        var json = { title: $(this).attr('data-name'), link: $(this).attr('data-link'), position: $(this).index() + 1 };
        dataResponse.push(json);
    });
    $('#menu_top').val(JSON.stringify(dataResponse));
}