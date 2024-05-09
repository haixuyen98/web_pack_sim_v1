var currentMenuEditItem = null;
window.addEventListener('load', function () {
    $('#mod_sortable').sortable({
        ghostClass: 'bg-success',
        animation: 150,
        stop: function (evt) {
            getSidebarRightJson();
        }
    });
    CKEDITOR.replace('module_content', {
        toolbarGroups: [{
            "name": "basicstyles",
            "groups": ["basicstyles"]
        },
        {
            "name": "links",
            "groups": ["links"]
        },
        {
            "name": "paragraph",
            "groups": ["list", "blocks"]
        },
        {
            "name": "document",
            "groups": ["mode"]
        },
        {
            "name": "insert",
            "groups": ["insert"]
        },
        {
            "name": "styles",
            "groups": ["styles"]
        }
        ],
        removePlugins: 'scayt,font,specialchar,blockquote,save,flash,iframe,pagebreak,templates,about,showblocks,newpage,language,print',
    });
})
function toggle_block(__this) {
    if (__this.find('i.la-eye').length) {
        __this.find('i.la-eye').removeAttr('class').addClass('las la-low-vision');
        __this.closest('.list-group-item').attr('data-hide', "1");
    } else {
        __this.find('i.la-low-vision').removeAttr('class').addClass('las la-eye');
        __this.closest('.list-group-item').attr('data-hide', "0");
    }
    getSidebarRightJson();
}


function remove_custom_module(__this) {
    __this.closest('.list-group-item').remove();
    getSidebarRightJson();
}
// function editModuleItem(__this) {
//     currentMenuEditItem = __this.closest('.list-group-item');
//     $('#form-custom-module').find('input[name="module_title"]').val(currentMenuEditItem.attr('data-content'));
//     $('#form-custom-module').find('textarea[name="module_content"]').val(currentMenuEditItem.attr('data-name'));
//     $('#sidebar-module-modal').modal('show');
// }
function addModuleItem(panelId) {
    el = document.getElementById(panelId);
    el.classList.remove('theme-editor__panel--is-visible')
    el.classList.remove('theme-editor__panel--is-active')
}
function saveModuleForm() {
    var moduleTitle = $('#form-custom-module').find('input[name="module_title"]').val();
    var hide_title = $('#form-custom-module').find("input[type='checkbox']:checked").val() == undefined ? '0' : '1';
    var moduleContent = CKEDITOR.instances["module_content"].getData();
    var editable = true;
    if (moduleTitle == '') {
        alert("Vui lòng điền tiêu đề menu");
        $('#form-custom-module').find('textarea[name="module_content"]').focus();
        return;
    }
    if (moduleContent == '') {
        alert("Vui lòng nhập nội dung");
        $('#form-custom-module').find('input[name="module_title"]').focus();
        return;
    }
    if (currentMenuEditItem == null) {
        var moduleHtml = `<div class="list-group-item" data-editable="`+editable+`" data-hide_title="`+hide_title+`" data-name="` + moduleTitle + `" data-content="` + moduleContent + `" data-hide="0" data-id="1">
        <div class="row">
          <div class="col-md-9 name">
                <img
                    class="icon_move"
                    src="https://doan.websim.vn/images/Move.png"
                    alt="" />
                <span class="mname">`+ moduleTitle + `</span>
            </div><div class="col-md-3 remove">
                    <a href="javascript:;" title="Xóa module" onclick="remove_custom_module($(this))"><i class="las la-trash-alt"></i></a>
                    <a
                        href="javascript:;"
                        title="Ẩn/Hiện module"
                        onclick="toggle_block($(this))"
                    ><i class="las la-eye"></i>
                    </a>
                </div>
        </div>
      </div>`;
        $('#mod_sortable').append(moduleHtml);
    } else {
        $(currentMenuEditItem).attr('data-name', moduleTitle);
        $(currentMenuEditItem).attr('data-content', moduleContent);
        $(currentMenuEditItem).attr('data-hide_title', hide_title);
        $(currentMenuEditItem).attr('data-editable', editable);
        $(currentMenuEditItem).find('.mname').html(moduleTitle);
        currentMenuEditItem = null;

    }
    getSidebarRightJson();
    $('#sidebar-module-modal').modal('hide');
    $('#sidebar-module-modal').find("input[type=text], textarea").val("");
}

function getSidebarRightJson() {
    var dataResponse = [];
    var element = $('#mod_sortable .list-group-item');
    $(element).parent().find('.list-group-item').each(function () {
        $(this).attr('data-id', $(this).index() + 1);
        var json = { title: $(this).attr('data-name'),editable: $(this).attr('data-editable'), hide_title: $(this).attr('data-hide_title'),content: $(this).attr('data-content'), is_hide: $(this).attr('data-hide'), position: $(this).index() + 1 };
        dataResponse.push(json);
    });
    $('#sidebar').val(JSON.stringify(dataResponse));
}