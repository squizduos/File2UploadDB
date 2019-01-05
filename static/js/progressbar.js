function _parse(str) {
    var args = [].slice.call(arguments, 1),
        i = 0;

    return str.replace(/%s/g, function() {
        return args[i++];
    });
}

function _extendDict(source, added) {
    for (var key in added) {
        if (key in source) {
            if (source[key] === undefined) {
                source[key] = added[key]
            }
        } else {
            source[key] = added[key];
        }            
    }
    return source
}

postgres_ajax_connector_default_values = {
    "ajax": {
        "url": "",
        "method": "GET",
        "beforeSend": function(){}
    },
    "fields": {
        "id_field": "id",
        "status_field": "status",
        "error_field": "error",
        "percent_field": "percent"
    },
    "texts": {
        "onReady": "",
        "onLaunch": "",
        "onMonitor": "",
        "onFinish": "",
        "onError": ""
    },
    "actions": {
        "onReady": function(){},
        "onLaunch": function(){},
        "onMonitor": function(){},
        "onFinish": function(){},
        "onError": function(){}
    }
}

class ProgressBarAJAXConnector {
    constructor(
        bar,
        configuration,
        timeout
    ) {
        this.bar = bar;
        this.startAjax = _extendDict(configuration['startAjax'], postgres_ajax_connector_default_values["ajax"]);
        this.monitorAjax = _extendDict(configuration['monitorAjax'], postgres_ajax_connector_default_values["ajax"]);
        this.fields = _extendDict(configuration['fields'], postgres_ajax_connector_default_values["fields"]);
        this.texts = _extendDict(configuration['texts'], postgres_ajax_connector_default_values["texts"]);
        this.actions = _extendDict(configuration['actions'], postgres_ajax_connector_default_values["actions"]);

        this.timeout = timeout;

        this.STATUS_READY = 0;
        this.STATUS_LAUNCH = 1;
        this.STATUS_FINISH = 2;
        this.STATUS_ERROR = 0;
    }

    setProgressBarState(state="ready", text="", percent=0) {
        if (state == "ready") {
            this.bar.removeClass("progress-bar-success");
            this.bar.removeClass("progress-bar-danger");
            this.bar.prop('aria-valuenow', 0);
            this.bar.prop('style', 'width: 0%');
            this.bar.children().text(text);
            this.actions.onReady();
        } else if (state == "finish") {
            this.bar.removeClass("progress-bar-danger");
            this.bar.addClass("progress-bar-success");
            this.bar.prop('aria-valuenow', 100);
            this.bar.prop('style', 'width: 100%');
            this.bar.children().text(text);
            this.actions.onFinish();
        } else if (state == "launch") {
            this.bar.removeClass("progress-bar-danger");
            this.bar.removeClass("progress-bar-success");
            this.bar.prop('aria-valuenow', percent);
            this.bar.prop('style', 'width:  ' + percent + '%');
            this.bar.children().text(text);
            this.actions.onMonitor();
        } else if (state == "error") {
            this.bar.addClass("progress-bar-danger");
            this.bar.removeClass("progress-bar-success");
            this.bar.prop('aria-valuenow', 0);
            this.bar.prop('style', 'width: 100%');
            this.bar.children().text(text);
            this.actions.onError();
        } else {
            console.log("Incorrect usage of setUploadProgressBar");
        }
    }
    
    started(data) {
        // Write launched info to class
        this.item_id = data[this.fields['id_field']];
        this.setProgressBarState("ready", this.texts.onLaunch);
        // Run custom action
        
        this.monitor(this);
    }

    start(item_id, data) {
        // Set bar as ready
        this.setProgressBarState("ready", this.textOnReady);
        // Make launch request
        var thisClass = this;
        $.ajax({
            beforeSend: this.startAjax.beforeSend,
            url: _parse(this.startAjax.url, item_id), 
            type: this.startAjax.method,
            data: data,
            success: function(data, textStatus, jqXHR) {
                thisClass.started(data);
            },
            error: function(requestObject, error, errorThrown) {
                thisClass.error(error);
            },
            dataType: "json",
        });                
    }
    
    monitor(thisClass = undefined) {
        if (thisClass === undefined) {
            thisClass = this;
        }
        $.ajax({
            beforeSend: thisClass.monitorAjax.beforeSend,
            url: _parse(thisClass.monitorAjax.url, this.item_id),
            type: thisClass.monitorAjax.method,
            success: function(data, textStatus, jqXHR) {      
                status = thisClass.process_data(data);
                if (status == thisClass.STATUS_LAUNCH) {
                    setTimeout(thisClass.monitor(thisClass), 5000)
                }
            },
            error: function(requestObject, error, errorThrown) {
                thisClass.error(error);
            },
            dataType: "json",
        });
        thisClass.actions.onMonitor();
    }
    
    process_data(data) {
        var status = data[this.fields['status_field']];
        var error_message = data[this.fields['error_field']];
        var percent = data[this.fields['percent_field']];
        switch(status) {
            case this.STATUS_ERROR:
                this.error(error_message);
                break;
            case this.STATUS_FINISH:
                this.finish(error_message);
                break;
            case this.STATUS_LAUNCH:
                this.launch(error_message, percent);
                break;
            default:
                this.error(error_message);
                break;
        }
        return status;
    }
    
    launch(err, percent) {
        var text = (this.texts['onMonitor'] ? this.texts['onMonitor'] : err);
        text = _parse(text, percent);
        this.setProgressBarState("launch", text, percent);
        this.actions.onError();
    }
    
    error(err) {
        var text = (this.texts['onError'] ? this.texts['onError'] : err);
        text = _parse(text, err);
        this.setProgressBarState("error", text);
        this.actions.onError();
    }
    
    finish(err) {
        var text = (this.texts['onFinish'] ? this.texts['onFinish'] : err);
        text = _parse(text, err);
        this.setProgressBarState("finish", text);
        this.actions.onFinish();
    }
}
