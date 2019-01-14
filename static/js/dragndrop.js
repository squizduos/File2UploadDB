$(document).ready(function () {
    function addNewFile(event) {
        $("input:file").change(function () {
            uploadFile(event);
        });
    }

    var dropZone = $('#dropZone'),
        selectedFile = $('#selectedFile'),
        maxFileSize = 1000000; // максимальный размер фалйа - 1 мб.

    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        selectedFile.text('Not supported by your browser!');
        selectedFile.addClass('error');
    }

    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function () {
        dropZone.addClass('hover');
        return false;
    };

    // Убираем класс hover
    dropZone[0].ondragleave = function () {
        dropZone.removeClass('hover');
        return false;
    };

    // Обрабатываем событие Drop
    dropZone[0].ondrop = function (event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');

        var file = event.dataTransfer.files[0];

        // Проверяем размер файла
        if (file.size > maxFileSize) {
            selectedFile.text('File is too big!');
            selectedFile.addClass('error');
            return false;
        }
        selectedFile.text(file.name);
        if ($('#agreeToRegulations')[0].checked) {
            $('#uploadFile').prop('disabled', false);
            $("#inputUploadFile")[0].files = event.dataTransfer.files;
            uploadFile(event);
        } else {
            selectedFile.text('Agree to document regulations first!');
            selectedFile.addClass('error');
        }
    };
});