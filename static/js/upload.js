$(document).ready(function() {
    // Defining constants
    var timeout = 1000;

    var extensions_config = {
        "CSV": {
            "file_header_line": "",
            "file_separator": ""
        },
        "XLS": {
            "file_header_line": "",
            "file_separator": "not applicable"
        },
        "XLSX": {
            "file_header_line": "",
            "file_separator": "not applicable"
        },
        "DTA": {
            "file_header_line": "not applicable",
            "file_separator": "not applicable"
        },
    }

    // Defining progress bar monitors

    uploadProgressBarMonitor = new ProgressBarAJAXConnector(
        $('#uploadProgressBar'),
        {
            "startAjax": {},
            "monitorAjax": {},
            "fields": {},
            "texts": {},
            "actions": {}
        },
        timeout
    );

    workProgressBarMonitor = new ProgressBarAJAXConnector(
        $('#workProgessBar'),
        {
            "startAjax": {
                "url": '/api/upload/%s/',
                "method": "PUT",
                "beforeSend": function(xhr) {
                    xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
                }
            },
            "monitorAjax": {
                "url": '/api/upload/%s/',
                "method": "GET",
                "beforeSend": function(xhr) {
                    xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
                }
            },
            "fields": {
                "id_field": "id"
            },
            "texts": {
                "onLaunch": "Starting upload...",
                "onMonitor": "Uploading %s%",
                "onFinish": "File uploaded successfully!",
                "onError": "Error uploading to DBMS: %s",
            },
            "actions": {
                "onFinish": function(){
                    $('#afterUploadToDB').prop('style', 'display: block'); 
                },
            }
        },
        timeout
    );;

    // UI elements behaviour

    $("input:file").change(function (){
        uploadFile(event);
    });

    $('#agreeToRegulations').change(function() {
        $('#uploadFile, #uploadStart').prop('disabled', !this.checked);
    });

    $('#file_type').on('change', function() {
        var extension = $(this).find(":selected").val();
        if ($("#file_id").val().length > 0) {  
            for (var key in extensions_config[extension]) {
                if (extensions_config[extension][key] == 'not applicable') {
                    $('#'+key).val(extensions_config[extension][key]);
                    $('#'+key).attr('readonly', 'readonly');
                } else {
                    $('#'+key).val('');
                    $('#'+key).removeAttr('readonly');
                }
            }
        }
    });

    $('#db_connection').on("change", function() {
        var selected = $(this).find(":selected").val();
        var form_data = {
            "db_connection": selected,
        };
        apiDecodeDBConnection(form_data, webFillDBForm);
    });

    $("#uploadStart").click(function (event){
        event.preventDefault();
        apiUploadFiletoDBMS(event);
    });

    $("#clearAll").click(function (event){
        event.preventDefault();
        apiDeleteFile(
            alertDeleteError,
            window.location.reload(false)
        );
    });

    $("#addNew").click(function (event){
        event.preventDefault();
        apiDeleteFile(
            alertDeleteError,
            webResetUploadFile 
        )
    });

    $('#removeFile').on('click', function(e) {
        e.preventDefault();
        apiDeleteFile(
            alertDeleteError,
            window.location.reload(false)
        );
    });

    // Upload file to server

    function uploadFile(event) {
        var fileName = $("input:file").val();
        var file = $("input:file")[0].files[0];
        var form_data = new FormData();
        form_data.append("document", file);
        var xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', uploadFileProgress, false);
        xhr.onreadystatechange = uploadFileFinished;
        xhr.open('POST', '/api/upload/');
        xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
        xhr.send(form_data);
        webSwitchUploadRemoveButton("remove");
    }
    
    function uploadFileProgress(event) {
        var percent = parseInt(event.loaded / event.total * 100);
        uploadProgressBarMonitor.setProgressBarState("launch", "", percent);
    }

    function uploadFileFinished(event) {
        if (event.target.readyState == 4) {
            if (event.target.status == 201) {
                var data = $.parseJSON(event.target.response);
                if (!data['error']) {
                    $("#table-info-form").autofill(data);
                    $("#file-info-form").autofill(data);
                    $("#db-info-form").autofill(data);
                    $.each(data, function(key, value){
                        editable = (data['enabled_for_editing'].indexOf(key) > -1);
                        webChangeEditing(key, editable, undefined)
                    });
                    uploadProgressBarMonitor.setProgressBarState("finish", "File is successfully uploaded!");
                    webSwitchUploadRemoveButton("remove");
                } else {
                    uploadProgressBarMonitor.setProgressBarState("error", "Error on uploading; try again later or check format!");    
                }
            } else {
                uploadProgressBarMonitor.setProgressBarState("error", "Error on uploading; try again later!");    
            }
        }
    }

    // API functions

    // Decode DB Connection
    function apiDecodeDBConnection(form_data, onSuccess, onError) {
        $.ajax({
            dataType: 'json',
            contentType: "application/json",
            data: JSON.stringify(form_data),
            url: "/api/utils/decode_db_connection/",
            type: "POST",
            success: onSuccess,
            error: onError
        }); 
    }
    
    // API: Delete file
    function apiDeleteFile(onError, onSuccess) {
        var file_id = $('[id=file_id]')[0].value;
        $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
            },
            dataType: 'json',
            contentType: "application/json",
            url: "/api/upload/"+file_id+"/",
            type: "DELETE",
            error: function(e) {
                onError();
            },
            success: function(data) {
                if (data['deleted'] == true) {
                    onSuccess();
                } else {
                    console.log(data);
                    onError();
                }
            },
        });
    }

    // API: Upload file to DBMS
    function apiUploadFiletoDBMS(event) {
        form_data = formValidateAndCollectData();
        if (form_data != undefined) {
            $('#workProgessBarDiv').prop('style', "display: block");
            workProgressBarMonitor.start(form_data.file_id, form_data);       
        } else {
            if(!form_data.file_id) {
                alert("You have to upload file before starting");
            }
        }
    }
    
    // API: Load connections list
    function apiLoadConnections(onSuccess, onError) {
        $.ajax({
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + getCookie('token'));
            },
            dataType: 'json',
            contentType: "application/json",
            url: "/api/utils/load_connections/",
            type: "GET",
            success: function(data) {
                onSuccess(data['connections'])
            },
            error: onError
        }); 
    }

    function formValidateAndCollectData() {
        var forms = ["file-info-form", "table-info-form", "db-info-form"];
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
            ignore: "[disabled=true]"
        };
        for (i in forms) {
            $("#"+forms[i]).validate(validateRules);
        }
        var valid = true;
        for (i in forms) {
            form_valid = $("#"+forms[i]).valid();
            valid = (form_valid == false ? false : valid);
        }
        if (valid) {
            var form_data = {};
            for (i in forms) {
                $("#"+forms[i]).serializeArray().map(
                    (el) => {form_data[el.name] = el.value}
                );
            }
            return form_data;                     
        } else {
            $("html, body").animate({ scrollTop: 0 }, "slow"); 
            return undefined;
        }
    }
    

    function webResetUploadFile() {
        $("#file-info-form input").val("");
        $("#file-upload-form input").val("");
        workProgressBarMonitor.setProgressBarState(state="ready")
        uploadProgressBarMonitor.setProgressBarState(state="ready")
        webSwitchUploadRemoveButton("upload");
        $("html, body").animate({ scrollTop: 0 }, "slow"); 
    }

    function webSwitchUploadRemoveButton(state){
        switch(state) {
            case "upload":
                $('#progessBarDiv').attr('hidden', 'hidden');
                $('#uploadButtonDiv').removeAttr('hidden');
                $('#removeButtonDiv').attr('hidden', 'hidden');
                break;
            case "remove":
                $('#progessBarDiv').removeAttr('hidden');
                $('#uploadButtonDiv').attr('hidden', 'true');
                $('#removeButtonDiv').removeAttr('hidden');
                break;
            default:
                console.log("Incorrect case");
                break;
        }
    }

    function webChangeEditing(element_id, editable) {
        element = $("#" + element_id);
        if (editable && element.attr('readonly')) {
            element.prop("placeholder", "");
            element.removeAttr('readonly');
        } else if (!editable && !element.attr('readonly')) {
            element.prop("readonly", "readonly");
        }
    }

    function webLoadConnections(connections) {
        selected = $("#db_connection").val();
        $("#db_connection").find('option').remove();
        $.each(connections, function (key, entry) {
            $("#db_connection").append(
                $('<option></option>').attr('value', entry.value).text(entry.name)
            );
        });
        $("#db_connection").val(selected);
    }

    function webFillDBForm(data) {
        $("#db-info-form").autofill(data);
        if ($("#db_type").val() == "PostgreSQL") {
            webChangeEditing("db_name", true, "");
            webChangeEditing("db_sid", false, "not applicable");
        } else if ($("#db_type").val() == "Oracle") {
            webChangeEditing("db_name", false, "not applicable");
            webChangeEditing("db_sid", true, "");
        }
    }

    // Load connections on start
    apiLoadConnections(webLoadConnections);

    function alertDeleteError() {
        alert("Can't delete file! If you want it, please contact administrator.")
    }
});