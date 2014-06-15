(function ($) {

    $.widget("cdm.base_versions_box",{
	options: {
	    prefix: "style",
	    editor_size: 6,
	    current_remove_classes: ["green"],
	    current_add_classes: ["blue"]
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";
	    var prefix_id="#"+opts.prefix+"-version-";

	    $("#"+opts.prefix+"-version-template").hide();
	    $("#"+opts.prefix+"-version-removed-template").hide();
	    $("#"+opts.prefix+"-version-form-text").santa_clara_editor({ textarea_id:opts.prefix+"-version-form-textarea",
									 textarea_name:"text",
									 editor_size: opts.editor_size
								       });
	    $(prefix_id+"form-valid").prop("checked",true);

	    /* add */

	    $("#"+opts.prefix+"-version-add-button").click(function(event){
		var url=$(prefix_id+"form").data("url");
		var data={};
		var vers_container=$("#"+opts.prefix+"-version-container");
		var num_versions=$(prefix_id+"container").data("num_versions");

		event.preventDefault();

		data["content_type"]=$(this).data("content_type");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-text").santa_clara_editor("get_text");
		data["valid"]=$(prefix_id+"form-valid").prop("checked");
		data["label"]=$(prefix_id+"form-label").val();

		if (!data["label"]){ 
		    var now=new Date();
		    var label="";
		    label+=now.getFullYear();
		    label+=('00'+(now.getMonth()+1)).slice(-2);
		    label+=('00'+now.getDate()).slice(-2);
		    label+=".";
		    label+=('00'+now.getHours()).slice(-2);
		    label+=('00'+now.getMinutes()).slice(-2);
		    label+=('00'+now.getSeconds()).slice(-2);
		    label+=".";
		    label+=('000000'+(1000*now.getMilliseconds())).slice(-6);
		    
		    data["label"]=label;
		}

		$.post(url,data)
		    .done( function(obj){
			vers_row=self._load_version(obj,vers_container);
			vers_row.show();
			$(prefix_id+"form-textarea").val("");
			$(prefix_id+"form-valid").prop("checked",true);
			num_versions+=1;
			$(prefix_id+"container").data("num_versions",num_versions);
			self._trigger("created",null,{"new":obj,"num_versions":num_versions});
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });
	},
	_update_version: function(vers){
	    var prefix_id="#"+this.options.prefix+"-version-";
	    var vers_text;
	    var vers_id=vers.id;
	    vers_text=$("<div/>").html(vers.text).text();
	    $(prefix_id+"text-"+vers.id).html(vers_text);
	    $(prefix_id+"last-modified-container-"+vers.id).show();
	    $(prefix_id+"last-modified-"+vers.id).html(vers.last_modified);
	    $(prefix_id+"last-modified-by-name-"+vers.id).attr("style","color:"+vers.modified_by.color);
	    $(prefix_id+"last-modified-by-name-"+vers.id).html(vers.modified_by.name);
	},
	_load_version: function(vers,container){
	    var vers_template=$("#"+this.options.prefix+"-version-template");
	    var vers_area;
	    var prefix_id="#"+this.options.prefix+"-version-";
	    var vers_text;
	    var self=this;

	    vers_area=vers_template.clone();
	    container.append(vers_area);

	    if (vers.is_current) {
		for(var i=0;i<this.options.current_remove_classes.length;i++)
		    vers_area.removeClass(this.options.current_remove_classes[i]);
		for(var i=0;i<this.options.current_add_classes.length;i++)
		    vers_area.addClass(this.options.current_add_classes[i]);
		this.current=vers;
	    }

	    vers_area.find("[id^="+this.options.prefix+"-version]").each(function(){
		if (!$(this).attr("id")) return;
		newid=$(this).attr("id")+"-"+vers.id;
		$(this).attr("id",newid);
	    });
	    vers_area.attr("id",vers_template.attr("id").replace("template","version-"+vers.id));
	    vers_area.data("vers_id",vers.id);

	    $(prefix_id+"save-button-"+vers.id)
		.data("content_type_id",vers.content_type_id)
		.data("object_id",vers.object_id);
	    $(prefix_id+"delete-button-"+vers.id).data("parent_id",this.options.prefix+"-version-version-"+vers.id);

	    $(prefix_id+"delete-button-"+vers.id).data("vers_id",vers.id);
	    $(prefix_id+"edit-button-"+vers.id).data("vers_id",vers.id);
	    $(prefix_id+"save-button-"+vers.id).data("vers_id",vers.id);
	    
	    $(prefix_id+"save-button-"+vers.id).hide();

	    if ( (vers.is_owner)||(vers.is_staff) ) {
		$(prefix_id+"save-button-"+vers.id).data("url",vers.json_update_url)
		$(prefix_id+"delete-button-"+vers.id).data("url",vers.json_delete_url);
		$(prefix_id+"edit-button-"+vers.id).show();
		if (vers.is_current) {
		    $(prefix_id+"delete-button-"+vers.id).hide();
		}
		else {
		    $(prefix_id+"delete-button-"+vers.id).show();
		}
	    }
	    else {
		$(prefix_id+"edit-button-"+vers.id).hide();
		$(prefix_id+"delete-button-"+vers.id).hide();
	    }


	    $(prefix_id+"created-"+vers.id).html(vers.created);
	    $(prefix_id+"created-by-avatar-"+vers.id).attr("src",vers.created_by.avatar);
	    $(prefix_id+"created-by-name-"+vers.id).attr("style","color:"+vers.created_by.color);
	    $(prefix_id+"created-by-name-"+vers.id).html(vers.created_by.name);

	    if ( (!vers.last_modified)||(vers.created==vers.last_modified) ){
		$(prefix_id+"last-modified-container-"+vers.id).hide();
	    }
	    else {
		$(prefix_id+"last-modified-container-"+vers.id).show();
		$(prefix_id+"last-modified-"+vers.id).html(vers.last_modified);
		$(prefix_id+"last-modified-by-name-"+vers.id).attr("style","color:"+vers.modified_by.color);
		$(prefix_id+"last-modified-by-name-"+vers.id).html(vers.modified_by.name);
	    }

	    if (vers.valid) {
		$(prefix_id+"valid-"+vers.id).show();
		$(prefix_id+"not-valid-"+vers.id).hide();
		$(prefix_id+"input-valid-"+vers.id).prop("checked",true);
	    }
	    else {
		$(prefix_id+"valid-"+vers.id).hide();
		$(prefix_id+"not-valid-"+vers.id).show();
		$(prefix_id+"input-valid-"+vers.id).prop("checked",false);
	    }
	    $(prefix_id+"input-valid-"+vers.id).hide();
	    $(prefix_id+"input-label-"+vers.id).val(vers.label);
	    $(prefix_id+"label-"+vers.id).html(vers.label);
	    $(prefix_id+"input-label-"+vers.id).hide();

	    vers_text=$("<div/>").html(vers.text).text();
	    $(prefix_id+"text-"+vers.id).html(vers_text);
	    
	    vers_text=$("<div/>").html(vers.raw_text).text();
	    $(prefix_id+"raw-text-"+vers.id).html(vers_text);
	    $(prefix_id+"raw-text-"+vers.id).santa_clara_editor({ textarea_id:this.options.prefix+"-version-form-textarea-"+vers.id,
								  textarea_name:"text",
								  editor_size: this.options.editor_size
								});

	    $(prefix_id+"raw-text-"+vers.id).hide();
	    $(prefix_id+"text-"+vers.id).show();

	    /* delete */
	    $(prefix_id+"delete-button-"+vers.id).click(function(event){
		var url=$(this).data("url");
		var vers_id=$(this).data("vers_id");
		var parent_id=$(this).data("parent_id");
		var num_versions=$(prefix_id+"container").data("num_versions");
		event.preventDefault();
		$.post(url,data={})
		    .done( function(obj){
			$("#"+parent_id).remove();
			num_versions-=1;
			$(prefix_id+"container").data("num_versions",num_versions);
			self._trigger("deleted",null,{"deleted_id":vers_id,"num_versions":num_versions});
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });

	    /* edit */
	    $(prefix_id+"edit-button-"+vers.id).click(function(event){
		event.preventDefault();
		$(prefix_id+"save-button-"+vers.id).show();
		$(prefix_id+"raw-text-"+vers.id).show();
		$(prefix_id+"text-"+vers.id).hide();
		$(prefix_id+"not-valid-"+vers.id).hide();
		$(prefix_id+"valid-"+vers.id).hide();
		$(prefix_id+"input-valid-"+vers.id).show();
		$(prefix_id+"label-"+vers.id).hide();
		$(prefix_id+"input-label-"+vers.id).show();
		$(this).hide();
	    });

	    /* save */
	    $(prefix_id+"save-button-"+vers.id).click(function(event){
		var url=$(this).data("url");
		var data={};
		event.preventDefault();
		data["content_type"]=$(this).data("content_type_id");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-textarea-"+vers.id).val();
		data["valid"]=$(prefix_id+"input-valid-"+vers.id).prop("checked");
		data["label"]=$(prefix_id+"input-label-"+vers.id).val();

		$.post(url,data)
		    .done( function(obj){
			self._update_version(obj);
			self._trigger("updated",null,obj);
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
		if (data["valid"]) {
		    $(prefix_id+"valid-"+vers.id).show();
		    $(prefix_id+"not-valid-"+vers.id).hide();
		}
		else {
		    $(prefix_id+"valid-"+vers.id).hide();
		    $(prefix_id+"not-valid-"+vers.id).show();
		}
		$(prefix_id+"input-valid-"+vers.id).hide();
		$(prefix_id+"label-"+vers.id).show();
		$(prefix_id+"input-label-"+vers.id).hide();
		$(prefix_id+"edit-button-"+vers.id).show();
		$(prefix_id+"raw-text-"+vers.id).hide();
		$(prefix_id+"text-"+vers.id).show();
		$(this).hide();
	    });

	    return vers_area;
	},
	load_object: function(obj){
	    var prefix_id="#"+this.options.prefix+"-version-";
	    var vers_container=$("#"+this.options.prefix+"-version-container");
	    var self=this;

	    $(prefix_id+"form-object-id").attr("value",obj.id);
	    $(prefix_id+"form-content-type").attr("value",obj.content_type_id);
	    $(prefix_id+"add-button").data("content_type",obj.content_type_id);
	    $(prefix_id+"add-button").data("object_id",obj.id);

	    this.element.find("div[id^="+this.options.prefix+"-version-version]").remove();

	    vers_container.data("num_versions",obj.versions.length);

	    for (i=0;i<obj.versions.length;i++){
		vers=obj.versions[i];
		vers_row=this._load_version(vers,vers_container);
		vers_row.show();
	    }
	    
	}, /* load_object */
	update_current: function(new_current_data){
	    var prefix_id="#"+this.options.prefix+"-version-";
	    var vers_id=new_current_data.id;
	    var vers_text="";

	    vers_text=$("<div/>").html(new_current_data.text).text();
	    $(prefix_id+"text-"+vers_id).html(vers_text);
	    
	    vers_text=$("<div/>").html(new_current_data.raw_text).text();
	    $(prefix_id+"raw-text-"+vers_id).html(vers_text);

	    $(prefix_id+"last-modified-container-"+vers_id).show();
	    $(prefix_id+"last-modified-"+vers_id).html(new_current_data.last_modified);
	    $(prefix_id+"last-modified-by-name-"+vers_id).attr("style","color:"+new_current_data.modified_by.color);
	    $(prefix_id+"last-modified-by-name-"+vers_id).html(new_current_data.modified_by.name);


	}, /* load_object */
	set_current: function(new_current){
	    var prefix_id="#"+this.options.prefix+"-version-";
	    var old_current=this.current;
	    if (new_current.id==old_current.id) {
		return;
	    }
	    $(prefix_id+"delete-button-"+new_current.id).hide();
	    $(prefix_id+"delete-button-"+old_current.id).show();
	    old_area=$(prefix_id+"version-"+old_current.id);
	    new_area=$(prefix_id+"version-"+new_current.id);
	    for(var i=0;i<this.options.current_remove_classes.length;i++){
		new_area.removeClass(this.options.current_remove_classes[i]);
		old_area.addClass(this.options.current_remove_classes[i]);
	    }
	    for(var i=0;i<this.options.current_add_classes.length;i++){
		new_area.addClass(this.options.current_add_classes[i]);
		old_area.removeClass(this.options.current_add_classes[i]);
	    }
	    this.current=new_current;
	}

    });

})(jQuery);