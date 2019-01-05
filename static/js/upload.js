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
        xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
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

    function changeEditing(element_id, editable) {
        element = $("#" + element_id);
        if (editable && element.attr('readonly')) {
            element.prop("placeholder", "");
            element.removeAttr('readonly');
        } else if (!editable && !element.attr('readonly')) {
            element.prop("readonly", "readonly");
        }
    }
    

    // Пост обрабочик
    function stateChange(event) {
        if (event.target.readyState == 4) {
            if (event.target.status == 201) {
                $('#uploadProgressBar').prop('aria-valuenow', 100);
                $('#uploadProgressBar').prop('style', 'width: 100%');
                var data = $.parseJSON(event.target.response);
                if (!data['error']) {
                    $("#table-info-form").autofill(data);
                    $("#file-info-form").autofill(data);
                    $("#db-info-form").autofill(data);
                    $.each(data, function(key, value){
                        console.log("key: " + key + " " + data['enabled_for_editing'].indexOf(key));
                        editable = (data['enabled_for_editing'].indexOf(key) > -1);
                        changeEditing(key, editable, undefined)
                      });
      
                    selectedFile.text('File is successfully uploaded!');
                    $('#uploadFile').on('click', function(e) {
                        e.preventDefault();
                        deleteFile(
                            event,
                            onSuccess=function(e) {
                                window.location.reload(false);
                            }
                        );
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

    function apiDecodeDBConnection(form_data) {
        $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
            },
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify(form_data),
            url: "/api/utils/decode_db_connection/",
            type: "POST",
            success: fillDBData
        }); 
    }
    
    // При выборе PostgreSQL лочится SID
    $('#db_connection').on("change", function() {
        var selected = $(this).find(":selected").val();
        var form_data = {
            "db_connection": selected,
        };
        apiDecodeDBConnection(form_data);
    });
    
    function loadConnections() {
        $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
            },
            dataType: 'json',
            contentType: "application/json",
            url: "/api/utils/load_connections/",
            type: "GET",
            success: function(data) {
                selected = $("#db_connection").val();
                $("#db_connection").find('option').remove();
                $.each(data['connections'], function (key, entry) {
                    $("#db_connection").append(
                        $('<option></option>').attr('value', entry.value).text(entry.name)
                    );
                });
                $("#db_connection").val(selected);
            }
        }); 
    }

    loadConnections();

    function fillDBData(data) {
        console.log("Autofill data: ");
        console.log(data);
        $("#db-info-form").autofill(data);
        console.log($("#db_type").val());
        if ($("#db_type").val() == "PostgreSQL") {
            console.log("Selected PostgreSQL!");
            changeEditing("db_name", true, "");
            changeEditing("db_sid", false, "not applicable");
        } else if ($("#db_type").val() == "Oracle") {
            console.log("Selected Oracle!");
            changeEditing("db_name", false, "not applicable");
            changeEditing("db_sid", true, "");
        }
    }



    // Загрузка файла
    $("#uploadStart").click(function (event){
        event.preventDefault();
        workWithFile(event);
    });

    function deleteFile(event, onError, onSuccess, onDone) {
        var file_id = $('[id=file_id]')[0].value;
        var request = $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
            },
            dataType: 'json',
            contentType: "application/json",
            url: "/api/upload/"+file_id+"/",
            type: "DELETE",
            error: onError,
            success: onSuccess,
            done: onDone,
            async: false,
        });
        request.done(function() {
            onDone();
        }); 
    }

    function validateAndCollectData() {
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
            $("#file-info-form").serializeArray().map(
                (el) => {
                    form_data[el.name] = el.value;
                }
            );
            $("#table-info-form").serializeArray().map(
                (el) => {
                    form_data[el.name] = el.value;
                }
            );
            $("#db-info-form").serializeArray().map(
                (el) => {
                    form_data[el.name] = el.value;
                }
            );
            return form_data;                     
        } else {
            return undefined;
        }
    }

    function sendStartUploadToDBMSRequest(form_data) {
        $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
            },
            dataType: 'json',
            contentType: "application/json",
            url: "/api/upload/" + form_data.file_id + '/',
            data: JSON.stringify(form_data),
            type: "PUT",
            error: workWithFileShowError,
            success: workWithFileCheckStatus(form_data.file_id),
        }); 
    }
    
    function workWithFile(event) {
        form_data = validateAndCollectData();
        if (form_data != undefined) {
            $('#workProgessBarDiv').prop('style', "display: block");
            sendStartUploadToDBMSRequest(form_data);         
        } else {
            if(!$("#file_id").val()) {
                alert("You have to upload file before starting");
            }
        }
    }

    function workWithFileShowError(error) {
        $('#workProgessBar').removeClass("progress-bar-success");
        $('#workProgessBar').addClass("progress-bar-danger");
        $('#workProgessBar').prop('aria-valuenow', 100);
        $('#workProgessBar').prop('style', 'width: 100%');
        $('#workProgessBarStatus').html(thrownError);            
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
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + localStorage.token);
            },
            url: "/api/upload/"+file_id+"/",
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
        deleteFile(
            event, 
            onError=function(err) {
                alert("Unabled to delete file due to techical reasons.");
                console.log(err);
            },
            onSuccess=function(data) {
                window.location.reload(false);
            },
        );
    });
    // Очистка путей в файле
    $("#addNew").click(function (event){
        event.preventDefault();
        deleteFile(
            event,
            onError=function(e) {
                alert("Unabled to delete file due to techical reasons.");
                alert(e);
            },
            onSuccess=function(data) {
                console.log("Successfully!");
            },
            onDone=resetUploadFile
        )
    });

    function resetUploadFile() {
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
    }

});