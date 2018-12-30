$(document).ready(function() {
    var selectedFile = $('#selectedFile');
    var timeout = 1000;

    function addNewFile(event) {
        $("input:file").change(function (){
            uploadFile(event);
        });
    }

    // Отображение файла при обычной загрузке
    $("input:file").change(function (){
        uploadFile(event);
    });

    // Разблокировка загрузчика при выборе галочки
    $('#agreeToRegulations').change(function() {
        if (this.checked) {
            $('#uploadFile').prop('disabled', false);
            $('#uploadStart').prop('disabled', false);
        } else {
            $('#uploadStart').prop('disabled', true);
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
                        console.log("key: " + key + " " + data['enabled_for_editing'].indexOf(key));
                        if (data['enabled_for_editing'].indexOf(key) > -1) {
                            $('#'+key).removeAttr('readonly');
                            $('#'+key).val(value);
                        } else {
                            $('#'+key).val("");
                            $('#'+key).prop("readonly", "readonly")
                            $('#'+key).prop('placeholder', value);      
                        }
                      });           
                    selectedFile.text('File is successfully uploaded!');
                    $('#uploadFile').on('click', function(e) {
                        e.preventDefault();
                        deleteFile(event);
                        window.location.reload(false);
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
                $('#file_header_line').removeAttr('readonly');
                $('#file_separator').val('');
                $('#file_separator').removeAttr('readonly');
            } else if ($(this).find(":selected").val() == 'XLS') {
                $('#file_header_line').val('');
                $('#file_header_line').removeAttr('readonly');
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('readonly', 'readonly');
            } else if ($(this).find(":selected").val() == 'XLSX') {
                $('#file_header_line').val('');
                $('#file_header_line').removeAttr('readonly');
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('readonly', 'readonly');

            } else if ($(this).find(":selected").val() == 'DTA') {
                $('#file_header_line').val('not applicable');
                $('#file_header_line').prop('readonly', 'readonly');
                $('#file_separator').val('not applicable');
                $('#file_separator').prop('readonly', 'readonly');
            }
        }
    });
    
    // При выборе PostgreSQL лочится SID
    $('#db_type').on("change", function() {
        if($(this).find(":selected").val() == 'PostgreSQL') {
            $('#db_sid').prop('placeholder', 'not applicable');
            $('#db_sid').prop('readonly', 'readonly');
        } else {
            $('#db_sid').prop('placeholder', '');
            $('#db_sid').removeAttr('readonly');
        }
    });



    // Загрузка файла
    $("#uploadStart").click(function (event){
        event.preventDefault();
        workWithFile(event);
    });

    function deleteFile(event) {
        var file_id = $('[id=file_id]')[0].value;
        var request = $.ajax({
            dataType: 'json',
            url: "/api/work/"+file_id+"/",
            type: "DELETE",
            error: function(e) {
                alert("Unabled to delete file due to techical reasons.");
                alert(e);
                return false;
            },
            success: function(data) {
                return true;
            },
            async: false,
        }); 
    }
    
    function workWithFile(event) {
        var validateRules = {
            highlight: function(element) {
                $(element).parent().addClass("has-error");
            },
            unhighlight: function(element) {
                $(element).parent().removeClass("has-error");
            },
            errorPlacement: function(error, element) {
                return false;
            },                      
            debug: true,
            ignore: "[readonly=readonly]"
        };
        $("#file-info-form").validate(validateRules);
        $("#table-info-form").validate(validateRules);
        $("#db-info-form").validate(validateRules);
        if ($("#file-info-form").valid() &&  $("#table-info-form").valid() && $("#db-info-form").valid()) {
            var form_data = {};
            data = $('[id*="db_"],[id*="file_"],[id*="table_"]').not('[readonly]');
            for (i = 0; i < data.length; i++) {
                form_data[data[i].id] = data[i].value;
            }
            $('#workProgessBarDiv').prop('style', "display: block");
            var request = $.ajax({
                dataType: 'json',
                url: "/api/work/",
                data: JSON.stringify(form_data),
                type: "POST",
                error: workWithFileShowError,
            }); 
            request.done(function(msg) {
                workWithFileCheckStatus(form_data.file_id);
            })
            request.fail(function(jqXHR, textStatus) {
                workWithFileShowError(textStatus);
            })         
        } else {
            alert("You have to upload file before starting");
        }
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
        $('#afterUploadToDB').prop('style', 'display: block');          
    }

    function workWithFileCheckStatus(file_id) {
        $.ajax({
            url: "/api/work/"+file_id+"/",
            type: "GET",
            success: function(data) {
                if (data['status'] == -1) {
                    workWithFileShowError(data['error']);
                }
                else if (data['status'] == 2) {
                    workWithFileShowSuccess();
                } else {
                    $('#workProgessBar').prop('aria-valuenow', data['percent']);
                    $('#workProgessBar').prop('style', 'width: '+data['percent']+'%');
                    if ('percent' in data) {
                        $('#workProgessBarStatus').html("Uploading " + data['percent'] + '%');
                    } else {
                        $('#workProgessBarStatus').html("Starting upload...");
                    }
                    setTimeout(function () {
                        workWithFileCheckStatus(file_id);
                    }, timeout)
                }
            },
            dataType: "json",
        });
                
    }
    
    // Очистка путей в файле
    $("#clearAll").click(function (event){
        event.preventDefault();
        var result = deleteFile();
        if (result === true) {
            window.location.reload(false);
        } else {
            window.location.reload(false);
        }
    });
    // Очистка путей в файле
    $("#addNew").click(function (event){
        event.preventDefault();
        var file_id = $('[id=file_id]')[0].value;
        var request = $.ajax({
            dataType: 'json',
            url: "/api/work/"+file_id+"/",
            type: "DELETE",
            error: function(e) {
                alert("Unabled to delete file due to techical reasons.");
                alert(e);
            },
            success: function(data) {
                console.log("Successfully!");
            },
            async: false,
        }); 
        request.done(function() {
            $('[id*="file_"]').each(function() {
                $(this).val('');
            });
            $('#workProgessBarStatus').html("");                
            $('#workProgressBar').removeClass("progress-bar-success");
            $('#workProgressBar').prop('aria-valuenow', 0);
            $('#workProgressBar').prop('style', 'width: 75%');
            $('#uploadProgressBar').removeClass("progress-bar-success");
            $('#uploadProgressBar').prop('aria-valuenow', 0);
            $('#progessBarDiv').prop('style', 'display: none');
            $('#uploadFile').html('<span id="uploadStatus">+ select file</span><input type="file" id="inputUploadFile" accept=".csv, .xls, .xlsx, .dta">');
            $('#uploadFile').prop('class', 'btn btn-lg btn-primary btn-file');   
            $('#uploadButtonDiv').prop('class', "col-lg-12");
            $('#uploadFile').prop('style', "width: 20%");
            $('#uploadButtonProgress').html('');
            $('#selectedFile').html('');
            $('#uploadFile').off('click');
            $('#uploadFile').on('click', function(e) {
                addNewFile(e);
            });
            $("html, body").animate({ scrollTop: 0 }, "slow");        
        });        
    });


    // function cloneFile(event) {
    //     var file_id = $('[id=file_id]')[0].value;
    //     var request = $.ajax({
    //         dataType: 'json',
    //         url: "/api/work/"+file_id+"/",
    //         type: "PUT",
    //         error: function() {
    //             console.log("Unabled to clone file due to techical reasons.");
    //             return false;
    //         },
    //         success: function(data) {
    //             return data['file_id'];
    //         }
    //     }); 
    // }

    // $('')
});