(function ($) {

    $.widget("cdm.base_comments_box",{
	options: {
	    prefix: "style",
	    editor_size: 6
	},
	_create: function(){
	    var self=this;
	    var el=self.element;
	    var opts=self.options;
	    var html="";
	    $("#"+opts.prefix+"-comment-template").hide();
	    $("#"+opts.prefix+"-comment-removed-template").hide();
	    $("#"+opts.prefix+"-comment-form-text").santa_clara_editor({ textarea_id:opts.prefix+"-comment-form-textarea",
									 textarea_name:"text",
									 editor_size: opts.editor_size
								       });
	    $("#"+opts.prefix+"-comment-add-button").click(function(event){
		var prefix_id="#"+opts.prefix+"-comment-";
		var url=$(prefix_id+"form").data("url");
		var data={};
		var comm_container=$("#"+opts.prefix+"-comment-container");
		event.preventDefault();

		data["content_type"]=$(this).data("content_type");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-textarea").val();

		$.post(url,data)
		    .done( function(obj){
			comm_row=self._load_comment(obj,comm_container);
			comm_row.show();
			$(prefix_id+"form-textarea").val("");
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });
	},
	_update_comment: function(comm){
	    var prefix_id="#"+this.options.prefix+"-comment-";
	    var comm_text;
	    var comm_id=comm.id;
	    comm_text=$("<div/>").html(comm.text).text();
	    $(prefix_id+"text-"+comm.id).html(comm_text);
	    $(prefix_id+"last-modified-container-"+comm.id).show();
	    $(prefix_id+"last-modified-"+comm.id).html(comm.last_modified);
	    $(prefix_id+"last-modified-by-name-"+comm.id).attr("style","color:"+comm.modified_by.color);
	    $(prefix_id+"last-modified-by-name-"+comm.id).html(comm.modified_by.name);
	},
	_load_comment: function(comm,container){
	    var comm_template=$("#"+this.options.prefix+"-comment-template");
	    var comm_removed_template=$("#"+this.options.prefix+"-comment-removed-template");
	    var comm_area;
	    var prefix_id="#"+this.options.prefix+"-comment-";
	    var comm_text;

	    if (comm.is_removed)
		comm_area=comm_removed_template.clone();
	    else
		comm_area=comm_template.clone();
	    container.append(comm_area);

	    comm_area.find("[id^="+this.options.prefix+"-comment]").each(function(){
		if (!$(this).attr("id")) return;
		newid=$(this).attr("id")+"-"+comm.id;
		$(this).attr("id",newid);
	    });
	    comm_area.attr("id",comm_template.attr("id").replace("template","comment-"+comm.id));
	    comm_area.data("comm_id",comm.id);

	    if (comm.is_removed) {
		comm_text=$("<div/>").html(comm.text).text();
		$(prefix_id+"text-"+comm.id).html(comm_text);
		return comm_area;
	    }

	    $(prefix_id+"save-button-"+comm.id)
		.data("content_type_id",comm.content_type_id)
		.data("object_id",comm.object_id);
	    $(prefix_id+"delete-button-"+comm.id).data("parent_id",this.options.prefix+"-comment-comment-"+comm.id);

	    $(prefix_id+"edit-button-"+comm.id).data("comm_id",comm.id);
	    $(prefix_id+"save-button-"+comm.id).data("comm_id",comm.id);
	    
	    if ( (comm.is_owner)||(comm.is_staff) ) {
		$(prefix_id+"save-button-"+comm.id).data("url",comm.json_update_url)
		$(prefix_id+"delete-button-"+comm.id).data("url",comm.json_delete_url);
	    }

	    $(prefix_id+"created-"+comm.id).html(comm.created);
	    $(prefix_id+"created-by-avatar-"+comm.id).attr("src",comm.created_by.avatar);
	    $(prefix_id+"created-by-name-"+comm.id).attr("style","color:"+comm.created_by.color);
	    $(prefix_id+"created-by-name-"+comm.id).html(comm.created_by.name);

	    if ( (!comm.last_modified)||(comm.created==comm.last_modified) ){
		$(prefix_id+"last-modified-container-"+comm.id).hide();
	    }
	    else {
		$(prefix_id+"last-modified-container-"+comm.id).show();
		$(prefix_id+"last-modified-"+comm.id).html(comm.last_modified);
		$(prefix_id+"last-modified-by-name-"+comm.id).attr("style","color:"+comm.modified_by.color);
		$(prefix_id+"last-modified-by-name-"+comm.id).html(comm.modified_by.name);
	    }

	    comm_text=$("<div/>").html(comm.text).text();
	    $(prefix_id+"text-"+comm.id).html(comm_text);
	    
	    comm_text=$("<div/>").html(comm.raw_text).text();
	    $(prefix_id+"raw-text-"+comm.id).html(comm_text);
	    $(prefix_id+"raw-text-"+comm.id).santa_clara_editor({ textarea_id:this.options.prefix+"-comment-form-textarea-"+comm.id,
								 textarea_name:"text",
								 editor_size: this.options.editor_size
							       });
	    $(prefix_id+"delete-button-"+comm.id).click(function(event){
		var url=$(this).data("url");
		var parent_id=$(this).data("parent_id");
		event.preventDefault();
		$.post(url,data={})
		    .done( function(obj){
			$("#"+parent_id).remove();
		    } )
		    .fail( function(data) {
			console.log("fail");
			console.log(data);
			console.log(data.responseText);
			alert(data.responseText+"\n"+data.getResponseHeader());
		    });
	    });
	    $(prefix_id+"edit-button-"+comm.id).click(function(event){
		event.preventDefault();
		$(prefix_id+"save-button-"+comm.id).show();
		$(prefix_id+"raw-text-"+comm.id).show();
		$(prefix_id+"text-"+comm.id).hide();
		$(this).hide();
	    });
	    var self=this;
	    $(prefix_id+"save-button-"+comm.id).click(function(event){
		var url=$(this).data("url");
		var data={};
		event.preventDefault();
		data["content_type"]=$(this).data("content_type_id");
		data["object_id"]=$(this).data("object_id");
		data["text"]=$(prefix_id+"form-textarea-"+comm.id).val();
		data["is_public"]=comm.is_public;
		data["is_removed"]=comm.is_removed;

		$.post(url,data)
		    .done( function(obj){
			self._update_comment(obj);
		    } )
		    .fail( function(ret) {
			console.log("fail");
			console.log(ret);
			console.log(ret.responseText);
			alert(ret.responseText+"\n"+ret.getResponseHeader());
		    });
		$(prefix_id+"edit-button-"+comm.id).show();
		$(prefix_id+"raw-text-"+comm.id).hide();
		$(prefix_id+"text-"+comm.id).show();
		$(this).hide();
	    });

	    $(prefix_id+"save-button-"+comm.id).hide();
	    if ( (comm.is_owner)||(comm.is_staff) ){
		$(prefix_id+"edit-button-"+comm.id).show();
		$(prefix_id+"delete-button-"+comm.id).show();
	    }
	    else {
		$(prefix_id+"edit-button-"+comm.id).show();
		$(prefix_id+"delete-button-"+comm.id).show();
	    }

	    $(prefix_id+"raw-text-"+comm.id).hide();
	    $(prefix_id+"text-"+comm.id).show();
	    return comm_area;
	},
	load_object: function(obj){
	    var prefix_id="#"+this.options.prefix+"-comment-";
	    var comm_container=$("#"+this.options.prefix+"-comment-container");
	    var self=this;

	    $(prefix_id+"form-object-id").attr("value",obj.id);
	    $(prefix_id+"form-content-type").attr("value",obj.content_type_id);
	    $(prefix_id+"add-button").data("content_type",obj.content_type_id);
	    $(prefix_id+"add-button").data("object_id",obj.id);

	    if (obj.can_add_comment)
		$(prefix_id+"form").show();
	    else
		$(prefix_id+"form").hide();
	    
	    this.element.find("div[id^="+this.options.prefix+"-comment-comment]").remove();

	    for (i=0;i<obj.comments.length;i++){
		comm=obj.comments[i];
		comm_row=this._load_comment(comm,comm_container);
		comm_row.show();
	    }
	    
	} /* load_object */

    });

})(jQuery);