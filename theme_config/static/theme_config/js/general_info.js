function updateImageName(input) {
    var uploadBox = input.closest('.upload-box');
    var imageNameInput = uploadBox.find('.input_image_value');
    var file = input[0].files[0];

    if (file) {
      imageNameInput.val(file.name);
    } else {
      imageNameInput.val('');
    }
  }

  $(document).ready(function () {
    $('.file-upload').on('change', function () {
      var input = $(this);
      var preview = input.closest('.upload-box').find('.preview');
      var file = input[0].files[0];

      if (file) {
        var reader = new FileReader();
        reader.onload = function (e) {
          preview.attr('src', e.target.result);
        };
        reader.readAsDataURL(file);

        updateImageName(input);
      }
    });

    function removeImage(element) {
      var uploadBox = element.closest('.upload-box');
      uploadBox.find('.file-upload').val('');
      uploadBox.find('.preview').attr('src', 'https://doan.websim.vn/images/system/default.jpg');
      updateImageName(uploadBox.find('.file-upload'));
    }

    $('.box-action a:contains("Xóa")').on('click', function () {
      removeImage($(this));
    });
  });