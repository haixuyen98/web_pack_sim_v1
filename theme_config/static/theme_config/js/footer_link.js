var currentFooterLinkEditItem = null;
window.addEventListener('load',function() {
    $('#footer_link-editor').sortable({
        ghostClass: 'bg-success',
        animation: 150,
        stop: function (evt) {
            getFooterLinkJson();
        }
    });
})
function removeFooterLinkItem(__this) {
    __this.closest('.list-group-item').remove();
    getFooterLinkJson();
}
function editFooterLinkItem(__this) {
    currentFooterLinkEditItem = __this.closest('.list-group-item');
    $('#form-add-footer_link').find('input[name="footer_link_name"]').val(currentFooterLinkEditItem.attr('data-name'));
    $('#form-add-footer_link').find('input[name="footer_link_link"]').val(currentFooterLinkEditItem.attr('data-link'));
    $('#footer_link-modal').modal('show');
}
function addFooterLinkItem(panelId) {
    el = document.getElementById(panelId);
    el.classList.remove('theme-editor__panel--is-visible')
    el.classList.remove('theme-editor__panel--is-active')
}
function saveFooterLinkForm() {
    var footerLinkUrl = $('#form-add-footer_link').find('input[name="footer_link_link"]').val();
    var footerLinkName = $('#form-add-footer_link').find('input[name="footer_link_name"]').val();
    if (footerLinkName == '') {
        alert("Vui lòng điền tiêu đề menu");
        $('#form-add-footer_link').find('input[name="footer_link_name"]').focus();
        return;
    }
    if (footerLinkUrl == '') {
        alert("Vui lòng nhập đường dẫn");
        $('#form-add-footer_link').find('input[name="footer_link_link"]').focus();
        return;
    }
    if (currentFooterLinkEditItem == null) {
        var footerLinkHtml = '<div class="list-group-item" data-name="' + footerLinkName + '" data-link="' + footerLinkUrl + '"><div class="row"><div class="col-md-9 name"><img class="icon_move" src="https://doan.websim.vn/images/Move.png" alt=""> <span class="mname">' + footerLinkName + '</span></div><div class="col-md-3 remove"><a href="javascript:void(0)" onclick="editfooter_linkItem($(this))"><i class="las la-pen"></i></a><a href="javascript:void(0)" onclick="removefooter_linkItem($(this))"><i class="las la-trash-alt"></i></a></div></div></div>';
        $('#footer_link-editor').append(footerLinkHtml);
    } else {
        $(currentFooterLinkEditItem).attr('data-name', footerLinkName);
        $(currentFooterLinkEditItem).attr('data-link', footerLinkUrl);
        $(currentFooterLinkEditItem).find('.mname').html(footerLinkName);
        currentFooterLinkEditItem = null;

    }
    getFooterLinkJson();
    $('#footer_link-modal').modal('hide');
    $('#footer_link-modal').find("input[type=text], textarea").val("");
}

function getFooterLinkJson() {
    var dataResponse = [];
    var element = $('#footer_link-editor .list-group-item');
    $(element).parent().find('.list-group-item').each(function () {
        $(this).attr('data-id', $(this).index() + 1);
        var json = { title: $(this).attr('data-name'), link: $(this).attr('data-link') };
        dataResponse.push(json);
    });
    $('#footer_link').val(JSON.stringify(dataResponse));
}