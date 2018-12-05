$(document).ready(function() {
    $('[data-toggle="popover"]').popover();

    var dropZone = $('#dropZone'),
        selectedFile = $('#selectedFile'),
        maxFileSize = 1000000; // максимальный размер фалйа - 1 мб.
    
    // Проверка поддержки браузером
    if (typeof(window.FileReader) == 'undefined') {
        selectedFile.text('Not supported by your browser!');
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


    // Отображение файла при обычной загрузке
    $("input:file").change(function (){
        uploadFile(event);
    });

    // Разблокировка загрузчика при выборе галочки
    $('#agreeToRegulations').change(function() {
        if (this.checked) {
            $('#uploadFile').prop('disabled', false);
        }
    });

    // Аплоад файла
    function uploadFile(event) {
        var fileName = $("input:file").val();
        var file = $("input:file")[0].files[0];

        var form_data = new FormData();
        form_data.append("document", file);

        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', uploadProgress, false);
        xhr.onreadystatechange = stateChange;
        xhr.open('POST', '/dashboard/');
        // xhr.setRequestHeader('X-FILE-NAME', file.name);
        xhr.send(form_data);
    }
    
    // Показываем процент загрузки
    function uploadProgress(event) {
        var percent = parseInt(event.loaded / event.total * 100);
        $('#progessBarDiv').prop('style', "display: block");
        $('#uploadButtonDiv').prop('class', "col-lg-3");
        $('#uploadFile').prop('style', "");

        $('#uploadProgressBar').prop('aria-valuenow', percent);
        $('#uploadProgressBar').prop('style', 'width: '+percent+'%');
        $('#uploadButtonProgress').html('Uploading '+percent+'%...');
    }
    
    // Пост обрабочик
    function stateChange(event) {
        if (event.target.readyState == 4) {
            if (event.target.status == 200) {
                $('#uploadProgressBar').prop('aria-valuenow', 100);
                $('#uploadProgressBar').prop('style', 'width: 100%');
                var data = $.parseJSON(event.target.response);
                if (!data['error']) {
                    $.each(data, function(key, value){
                        $('#'+key).val(value);
                      });  
                    $.each(data['enabled_for_editing'], function(key, value){
                        $('#'+value).prop('disabled', false);
                      });                
                    selectedFile.text('File is successfully uploaded!');
                    $('#uploadFile').prop('onClick', "function(e) {window.location.reload(false)}");
                    $('#uploadFile').html('Remove');
                    $('#uploadFile').prop('class', 'btn btn-danger btn-lg');    
                } else {
                    $('#uploadProgressBar').removeClass("progress-bar-success");
                    $('#uploadProgressBar').addClass("progress-bar-danger");
                    selectedFile.text('Error on uploading; try again later or check format!');
                    selectedFile.addClass('error');    
                }
            } else {
                $('#uploadProgressBar').removeClass("progress-bar-success");
                $('#uploadProgressBar').addClass("progress-bar-danger");
                selectedFile.text('Error on uploading; try again later!');
                selectedFile.addClass('error');
            }
        }
    }
    
});

$(function() {

 });
