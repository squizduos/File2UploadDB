$(document).ready(function() {
    $('[data-toggle="popover"]').popover();

    var dropZone = $('#dropZone'),
        selectedFile = $('#selectedFile'),
        maxFileSize = 1000000; // максимальный размер фалйа - 1 мб.
    
    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        selectedFile.text('Не поддерживается браузером!');
        selectedFile.addClass('error');
    }
    
    // Добавляем класс hover при наведении
    dropZone[0].ondragover = function() {
        dropZone.addClass('hover');
        return false;
    };
    
    // Убираем класс hover
    dropZone[0].ondragleave = function() {
        dropZone.removeClass('hover');
        return false;
    };
    
    // Обрабатываем событие Drop
    dropZone[0].ondrop = function(event) {
        event.preventDefault();
        dropZone.removeClass('hover');
        dropZone.addClass('drop');
        
        var file = event.dataTransfer.files[0];
        
        // Проверяем размер файла
        if (file.size > maxFileSize) {
            dropZone.text('Файл слишком большой!');
            dropZone.addClass('error');
            return false;
        }
        selectedFile.text(file.name);
        if ($('#agreeToRegulations').checked) {
            $('#uploadStart').prop('disabled', false);
        }
    };


    // Отображение файла при обычной загрузке
    $("input:file").change(function (){
        var fileName = $(this).val();
        $('#selectedFile').text(fileName);
        if ($('#agreeToRegulations').checked) {
            $('#uploadStart').prop('disabled', false);
        }
    });

    // Разблокировка загрузчика при выборе галочки
    $('#agreeToRegulations').change(function() {
        if (this.checked && selectedFile.text().length > 0) {
            $('#uploadStart').prop('disabled', false);
        }
    });

    // Аплоад файла
    function uploadFile(event) {
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', uploadProgress, false);
        xhr.onreadystatechange = stateChange;
        xhr.open('POST', '/upload.php');
        xhr.setRequestHeader('X-FILE-NAME', file.name);
        xhr.send(file);
    }
    
    // Показываем процент загрузки
    function uploadProgress(event) {
        var percent = parseInt(event.loaded / event.total * 100);
        dropZone.text('Загрузка: ' + percent + '%');
    }
    
    // Пост обрабочик
    function stateChange(event) {
        if (event.target.readyState == 4) {
            if (event.target.status == 200) {
                dropZone.text('Загрузка успешно завершена!');
                ("#file_storage").text("Temporary - deleted after import to database");
            } else {
                dropZone.text('Произошла ошибка!');
                dropZone.addClass('error');
            }
        }
    }
    
});

$(function() {

 });
