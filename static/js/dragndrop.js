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
        } else {
            if ($("#uploadFile").text() != "Remove") {
                $('#uploadFile').prop('disabled', true);
            }
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
        xhr.open('POST', '/api/upload/');
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
                    $('#uploadFile').on('click', function(e) {
                        e.preventDefault();
                        clearFile(event);
                    });
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

    $('#file_type').on('change', function() {
        if ($("#uploadFile").text() == "Remove") {        
            if($(this).find(":selected").val() == 'CSV') {
                $('#file_header_line').val('');
                $('#file_header_line').prop('disabled', false);
                $('#file_separator').val('');
                $('#file_separator').prop('disabled', false);
            } else if ($(this).find(":selected").val() == 'XLS') {
                $('#file_header_line').val('');
                $('#file_header_line').prop('disabled', false);
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('disabled', true);
            } else if ($(this).find(":selected").val() == 'XLSX') {
                $('#file_header_line').val('');
                $('#file_header_line').prop('disabled', false);
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('disabled', true);

            } else if ($(this).find(":selected").val() == 'DTA') {
                $('#file_header_line').val('not applicable');
                $('#file_header_line').prop('disabled', true);
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('disabled', true);
            }
        }
    });
    
    // При выборе PostgreSQL лочится SID
    $('#db_type').on("change", function() {
        if($(this).find(":selected").val() == 'PostgreSQL') {
            $('#db_sid').val('not applicable');
            $('#db_sid').prop('disabled', true);
        } else {
            $('#db_sid').val('');
            $('#db_sid').prop('disabled', false);
        }
    });

    // Проверяем заполненность полей формы
    function validateForm() {
        var isValid = true;
        $('[id*="db_"],[id*="file_"],[id*="table_"]').each(function() {
          if ( $(this).val() === '' )
              isValid = false;
        });
        return isValid;
      }
      
    // Разблокировка при заполнении всех полей
    $('[id*="db_"],[id*="file_"],[id*="table_"]').on("change keyup paste", function() {
        if(validateForm()) {
            $('#uploadStart').prop('disabled', false);
        }
    });

    var working = false;

    // Загрузка файла
    $("#uploadStart").click(function (event){
        event.preventDefault();
        workWithFile(event);
    });

    function clearFile(event) {
        var file_id = $('[id=file_id]')[0].value;
        var request = $.ajax({
            dataType: 'json',
            url: "/api/work/cancel/"+file_id,
            type: "GET",
            error: workWithFileShowError,
        }); 
        request.done(function(msg) {
            window.location.reload(false);
        })
    }
    
    function workWithFile(event) {
        var form_data = {};
        data = $('[id*="db_"],[id*="file_"],[id*="table_"]');
        for (i = 0; i < data.length; i++) {
            form_data[data[i].id] = data[i].value;
        }
        $('#workProgessBarDiv').prop('style', "display: block");
        var request = $.ajax({
            dataType: 'json',
            url: "/api/work/start",
            data: JSON.stringify(form_data),
            type: "POST",
            error: workWithFileShowError,
        }); 
        request.done(function(msg) {
            working = true;
            workWithFileCheckStatus(form_data['file_id']);
        })
        request.fail(function(jqXHR, textStatus) {
            workWithFileShowError(textStatus);
        })         
    }

    function workWithFileShowError(error) {
        $('#workProgessBar').removeClass("progress-bar-success");
        $('#workProgessBar').addClass("progress-bar-danger");
        $('#workProgessBar').prop('aria-valuenow', 100);
        $('#workProgessBar').prop('style', 'width: 100%');
        $('#workProgessBarStatus').html(error);            
    }

    function workWithFileShowSuccess() {
        $('#workProgessBar').removeClass("progress-bar-danger");
        $('#workProgessBar').addClass("progress-bar-success");
        $('#workProgessBar').prop('aria-valuenow', 100);
        $('#workProgessBar').prop('style', 'width: 100%');
        $('#workProgessBarStatus').html('Uploaded successfully!');            
    }

    function workWithFileCheckStatus(file_id) {
        if (working) {
            setTimeout(function() {
                $.ajax({
                    url: "/api/work/check/"+file_id,
                    type: "GET",
                    success: function(data) {
                        if (data['percent'] == 100) {
                            working = false;
                        }
                        if (data['status'] == -1) {
                            workWithFileShowError(data['error']);
                        }
                        else if (data['status'] == 2) {
                            workWithFileShowSuccess();
                        } else {
                            $('#workProgessBar').prop('aria-valuenow', data['percent']);
                            $('#workProgessBar').prop('style', 'width: '+data['percent']+'%');
                            $('#workProgessBarStatus').html("Uploading " + data['percent'] + '%');                
                        }
                    },
                    dataType: "json",
                    complete: workWithFileCheckStatus(file_id),
                    timeout: 2000
                })
            }, 1000);    
        }        
    }
    
    // Очистка путей в файле
    $("#clearAll").click(function (event){
        event.preventDefault();
        $('[id*="db_"],[id*="file_"],[id*="table_"]').each(function() {
            $(this).val('')
        });
    });

});


$('body').on('click', function (e) {
    if ($(e.target).data('toggle') !== 'popover'
        && $(e.target).parents('.popover.in').length === 0) { 
        $('[data-toggle="popover"]').popover('hide');
    }
});